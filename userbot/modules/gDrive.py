"""
GDrive Client Module for Userbot

Usage:- .drivesearch search_query
        .drivedl drive_link
        .gdrive filePath/replyToMessage
        .drivemeta drive_link

Author:- Git: github.com/jaskaranSM | Tg:  https://t.me/Zero_cool7870
"""

import asyncio
import math
import mimetypes
import os
import pickle
import re
import time
import urllib.parse as urlparse
from datetime import datetime
from urllib.parse import parse_qs

import aiofiles
import aiohttp
from gaggle import Client
from googleapiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow
from sample_config import Config
from telethon import events
from telethon.errors.rpcerrorlist import MessageNotModifiedError
from userbot import bot
from userbot.database.mongo import cli
from userbot.util import admin_cmd, humanbytes, progress, time_formatter

from google.auth.transport.requests import Request

space = '    '
branch = '│   '
tee = '├── '
last = '└── '


db = cli["Userbot"]
G_DRIVE_TOKEN_FILE = "token.pickle"
driveDB = db.GDRIVE
SLEEP_TIME = 5
G_DRIVE_DIR_MIME_TYPE = "application/vnd.google-apps.folder"


def getAccessTokenDB():
    cursor = driveDB.find()
    for c in cursor:
        return c.get("access_token")
    return b""


def saveAccessTokenDB(token):  # bytes
    print("Updating Access Token in Database")
    previousToken = getAccessTokenDB()
    cur_filter = {"access_token": previousToken}
    driveDB.update_one(
        cur_filter, {'$set': {"access_token": token}}, upsert=True)


def InitGDrive():
    if not os.path.exists(G_DRIVE_TOKEN_FILE):
        print("Fetching Access Token from Database")
        token = getAccessTokenDB()
        if len(token) == 0:
            return
        with open(G_DRIVE_TOKEN_FILE, "wb") as f:
            f.write(token)


InitGDrive()


def getProgressBarString(percentage):
    return "[{0}{1}]\n".format(
        ''.join("▰" for i in range(math.floor(percentage / 5))),
        ''.join("▱" for i in range(18 - math.floor(percentage / 5))),
    )


async def progressSpinner(drive_obj, banner, event):
    while not drive_obj.isComplete():
        text = f"__{banner}__\n"
        try:
            text += getProgressString(drive_obj)
        except Exception as e:
            text += str(e)
        try:
            if text != drive_obj.previous_msg_text:
                await event.edit(text)
                drive_obj.previous_msg_text = text
        except MessageNotModifiedError:
            pass
        await asyncio.sleep(SLEEP_TIME)


def getProgressString(drive_obj):
    progressStr = f"**Transferred:** `{humanbytes(drive_obj.transferredBytes())}`\n"
    progressStr += f"`{getProgressBarString(drive_obj.percent())}`"
    progressStr += f"**Percent:** `{drive_obj.percent()}%\n`"
    progressStr += f"**Speed:** `{humanbytes(drive_obj.speed())}ps`\n"
    progressStr += f"**ETA:** `{time_formatter(drive_obj.eta())}`\n"
    progressStr += f"**Total:** `{humanbytes(drive_obj.totalBytes())}`\n"
    return progressStr


async def postTextToDogBin(text):
    async with aiohttp.ClientSession() as session:
        async with session.post('https://nekobin.com/api/documents', json={"content": text}) as response:
            respJson = await response.json()
            return f"https://nekobin.com/{respJson.get('result').get('key')}.py"


class Folder:
    def __init__(self, obj):
        self.name = obj.get('name')
        self.size = 0
        self.mimeType = obj.get('mimeType')
        self.id = obj.get('id')
        self.children = []

    def calculateSize(self, children):
        for file in children:
            if file.mimeType == G_DRIVE_DIR_MIME_TYPE:
                file.size = 0
                file.calculateSize(file.children)
                self.calculateSize(file.children)
            else:
                self.size += int(file.size)

    def addChild(self, child):
        self.children.append(child)

    def addChildByFolderId(self, node, folder_id, child):
        if folder_id == node.id:
            return node.addChild(child)
        for child_node in node.children:
            if child_node.mimeType == G_DRIVE_DIR_MIME_TYPE:
                self.addChildByFolderId(child_node, folder_id, child)


class File:
    def __init__(self, obj):
        self.name = obj.get('name')
        self.size = int(obj.get('size') or 0)
        self.mimeType = obj.get('mimeType')
        self.id = obj.get('id')
        self.obj = obj


class GDriveHelper:
    def __init__(self):
        self.service = None
        self.session = aiohttp.ClientSession()
        self.SCOPES = ['https://www.googleapis.com/auth/drive']
        self.G_DRIVE_DIR_MIME_TYPE = "application/vnd.google-apps.folder"
        self.__REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
        self.__G_DRIVE_BASE_DOWNLOAD_URL = "https://drive.google.com/uc?id={}&export=download"
        self.__G_DRIVE_DIR_BASE_DOWNLOAD_URL = "https://drive.google.com/drive/folders/{}"
        self.chunksize = 50*1024*1024
        self.file_count = 0
        self.is_complete = False
        self.previous_msg_text = ""
        self.size = 0
        self.transferred_bytes = 0
        self._eta = 0
        self.total_bytes = 0
        self.transfer_speed = 0
        self.start_time = time.time()
        self.root_node = None
        self.SLEEP_TIME = 1
        self.sem = asyncio.Semaphore(5)

    def getRootNode(self):
        return self.root_node

    def setRootNode(self, node):
        self.root_node = node

    def speed(self):
        return self.transfer_speed

    def percent(self):
        try:
            return round(self.transferredBytes() * 100 / self.totalBytes(), 2)
        except ZeroDivisionError:
            return 0.0

    def eta(self):
        return self._eta

    def totalBytes(self):
        return self.total_bytes

    def transferredBytes(self):
        return self.transferred_bytes

    def isComplete(self):
        return self.is_complete

    @staticmethod
    def getSizeLocal(path):
        if os.path.isfile(path):
            return os.path.getsize(path)
        total_size = 0
        for root, dirs, files in os.walk(path):
            for f in files:
                abs_path = os.path.join(root, f)
                total_size += os.path.getsize(abs_path)
        return total_size

    async def getSizeDriveFolder(self, folder_id):
        files = await self.getFilesByParentId(folder_id)
        for file in files:
            if file.get("mimeType") == self.G_DRIVE_DIR_MIME_TYPE:
                await self.getSizeDriveFolder(file.get('id'))
            else:
                self.file_count += 1
                self.size += int(file.get('size') or 0)

    async def getSizeDrive(self, file_id):
        self.size = 0
        meta = await self.getMetadata(file_id)
        if meta.get("mimeType") == self.G_DRIVE_DIR_MIME_TYPE:
            await self.getSizeDriveFolder(meta.get('id'))
            return self.size
        else:
            self.file_count += 1
            return int(meta.get("size") or 0)

    def onTransferComplete(self):
        print("onTransferComplete...")
        self.is_complete = True

    def onProgressUpdate(self, chunkSize):
        self.transferred_bytes += chunkSize
        diff = time.time() - self.start_time
        self.transfer_speed = self.transferredBytes() / diff
        try:
            self._eta = round(
                (self.totalBytes() - self.transferredBytes()) / self.speed()) * 1000
        except ZeroDivisionError:
            self._eta = 0

    async def getCreds(self, event=None):
        credentials = None
        if os.path.exists(G_DRIVE_TOKEN_FILE):
            with open(G_DRIVE_TOKEN_FILE, 'rb') as f:
                credentials = pickle.load(f)
        if credentials is None or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                with open(G_DRIVE_TOKEN_FILE, "rb") as token:
                    saveAccessTokenDB(token.read())
                with open(G_DRIVE_TOKEN_FILE, "wb") as token:
                    pickle.dump(credentials, token)
            else:
                flow = OAuth2WebServerFlow(
                    Config.G_DRIVE_CLIENT_ID,
                    Config.G_DRIVE_CLIENT_SECRET,
                    self.SCOPES,
                    redirect_uri=self.__REDIRECT_URI
                )
                authorize_url = flow.step1_get_authorize_url()
                code = ""
                print(authorize_url)
                if event:
                    async with event.client.conversation(Config.PRIVATE_GROUP_BOT_API_ID) as conv:
                        await conv.send_message(f"Go to the following link in your browser: {authorize_url} and reply the code")
                        response = conv.wait_event(events.NewMessage(
                            outgoing=True,
                            chats=Config.PRIVATE_GROUP_BOT_API_ID
                        ))
                        response = await response
                        code = response.message.message.strip()
                else:
                    code = input("Enter CODE: ")
                creds = flow.step2_exchange(code)
                credentials = Client._make_credentials(token=creds.access_token, refresh_token=creds.refresh_token, id_token=creds.id_token,
                                                       token_uri=creds.token_uri, client_id=creds.client_id, client_secret=creds.client_secret)
                with open(G_DRIVE_TOKEN_FILE, 'wb') as token:
                    pickle.dump(credentials, token)
                with open(G_DRIVE_TOKEN_FILE, "rb") as token:
                    saveAccessTokenDB(token.read())
        return credentials

    async def authorize(self, event=None):
        creds = await self.getCreds(event)
        self.service = Client(session=self.session,
                              credentials=creds).drive("v3")

    @staticmethod
    def getFileOps(file_path):
        mime_type = mimetypes.guess_type(file_path)[0]
        mime_type = mime_type or "text/plain"
        file_name = file_path.rsplit("/", 1)[-1]
        return file_name, mime_type

    async def setPermissions(self, file_id):
        permissions = {
            'role': 'reader',
            'type': 'anyone',
            'value': None,
            'withLink': True
        }
        return await self.service.permissions.create(supportsTeamDrives=True, fileId=file_id, body=permissions)

    async def fileSender(self, file_name=None):
        async with aiofiles.open(file_name, 'rb') as f:
            chunk = await f.read(self.chunksize)
            while chunk:
                self.onProgressUpdate(len(chunk))
                yield chunk
                chunk = await f.read(self.chunksize)

    async def uploadFile(self, file_path, parent_id=None):
        file_name, mime_type = self.getFileOps(file_path)
        file_metadata = {
            'name': file_name,
            'description': 'userbot',
            'mimeType': mime_type,
        }
        if parent_id is not None:
            file_metadata['parents'] = [parent_id]

        media_body = MediaFileUpload(file_path,
                                     mimetype=mime_type,
                                     resumable=True,
                                     chunksize=self.chunksize)
        response = await self.service.files.create(supportsTeamDrives=True,
                                                   body=file_metadata, media_body=media_body)

        uploadLocation = response.headers.get("location")
        file_id = ""
        async with self.session.put(uploadLocation, data=self.fileSender(file_path), timeout=None) as resp:
            resJson = await resp.json()
        file_id = resJson.get("id")
        if not Config.IS_TEAM_DRIVE:
            await self.setPermissions(file_id)
        return file_id

    async def createDirectory(self, directory_name, parent_id=None):
        file_metadata = {
            "name": directory_name,
            "mimeType": self.G_DRIVE_DIR_MIME_TYPE
        }
        if parent_id is not None:
            file_metadata["parents"] = [parent_id]
        response = await self.service.files.create(supportsTeamDrives=True,
                                                   body=file_metadata)

        resJson = await response.json()
        if not Config.IS_TEAM_DRIVE:
            await self.setPermissions(resJson.get('id'))
        return resJson.get("id")

    async def uploadFolder(self, input_directory, folder_id=None):
        files = os.listdir(input_directory)
        if len(files) == 0:
            return None
        for file in files:
            absPath = os.path.join(input_directory, file)
            if os.path.isdir(absPath):
                newDir = await self.createDirectory(file, folder_id)
                await self.uploadFolder(absPath, newDir)
            else:
                await self.uploadFile(absPath, folder_id)

    async def upload(self, file_path, event):
        await event.edit("Calculating Size please wait!")
        size = self.getSizeLocal(file_path)
        self.total_bytes = size
        link = ""
        if os.path.isdir(file_path):
            dir_id = await self.createDirectory(self.getFileName(file_path), Config.GDRIVE_FOLDER_ID)
            await self.uploadFolder(file_path, dir_id)
            link = self.formatLink(dir_id)
        else:
            file_id = await self.uploadFile(file_path, Config.GDRIVE_FOLDER_ID)
            link = self.formatLink(file_id, folder=False)
        self.onTransferComplete()
        return link

    def formatLink(self, id, folder=True):
        if folder:
            return self.__G_DRIVE_DIR_BASE_DOWNLOAD_URL.format(id)
        return self.__G_DRIVE_BASE_DOWNLOAD_URL.format(id)

    @staticmethod
    def parseLink(link):
        if "folders" in link or "file" in link:
            regex = r"https://drive\.google\.com/(drive)?/?u?/?\d?/?(mobile)?/?(file)?(folders)?/?d?/([-\w]+)[?+]?/?(w+)?"
            res = re.search(regex, link)
            if res is None:
                raise IndexError("GDrive ID not found.")
            return res.group(5)
        parsed = urlparse.urlparse(link)
        return parse_qs(parsed.query)['id'][0]

    async def downloadFolder(self, folder_id, local_path):
        files = await self.getFilesByParentId(folder_id)
        for file in files:
            newPath = os.path.join(local_path, file.get("name"))
            if file.get("mimeType") == self.G_DRIVE_DIR_MIME_TYPE:
                os.makedirs(newPath, exist_ok=True)
                await self.downloadFolder(file.get("id"), newPath)
            else:
                await self.downloadFile(file.get("id"), newPath)

    async def download(self, file_id, event):
        await event.edit("Calculating Size please wait!")
        size = await self.getSizeDrive(file_id)
        self.total_bytes = size
        meta = await self.getMetadata(file_id)
        if meta.get('mimeType') == self.G_DRIVE_DIR_MIME_TYPE:
            os.makedirs(meta.get('name'), exist_ok=True)
            await self.downloadFolder(meta.get('id'), meta.get('name'))
        else:
            await self.downloadFile(meta.get('id'), meta.get('name'))
        self.onTransferComplete()
        return meta.get('name')

    async def getAccessToken(self):
        return (await self.getCreds()).token

    @staticmethod
    def getFileName(file_path):
        return file_path.rsplit("/", 1)[-1]

    async def getMetadata(self, file_id):
        file_metadata = await self.service.files.get(supportsAllDrives=True, fileId=file_id, fields="*")
        return await file_metadata.json()

    async def downloadFile(self, file_id, file_path):
        uri = f"https://www.googleapis.com/drive/v3/files/{file_id}"
        creds = await self.getCreds()
        creds.refresh(Request())
        access_token = creds.token
        queryString = {
            "includeItemsFromAllDrives": "true",
            "supportsAllDrives": "true",
            "alt": 'media',
            "includeTeamDriveItems": "true"
        }
        headers = {"accept-encoding": 'gzip;q=0,deflate,sdch',
                   'authorization': f'Bearer {access_token}'}
        response = await self.session.get(uri, params=queryString, headers=headers, timeout=None)
        with open(file_path, "wb") as file_writer:
            async for chunk, _ in response.content.iter_chunks():
                file_writer.write(chunk)
                file_writer.flush()
                self.onProgressUpdate(len(chunk))

    async def traverseFolder(self, folder_id):
        files = await self.getFilesByParentId(folder_id)
        async with self.sem:
            reqs = []
            for file in files:
                if file.get('mimeType') == self.G_DRIVE_DIR_MIME_TYPE:
                    folder = Folder(file)
                    self.root_node.addChildByFolderId(
                        self.getRootNode(), folder_id, folder)
                    reqs.append(self.traverseFolder(file.get('id')))
                else:
                    f = File(file)
                    self.root_node.addChildByFolderId(
                        self.getRootNode(), folder_id, f)
                    self.size += int(file.get('size') or 0)
                    self.file_count += 1
            if len(reqs) != 0:
                await asyncio.wait(reqs)

    async def copyFile(self, file_id, dest_id):
        body = {
            'parents': [dest_id]
        }
        res = await self.service.files.copy(supportsAllDrives=True, fileId=file_id, body=body)
        resJson = await res.json()
        file_id = resJson.get('id')
        if not Config.IS_TEAM_DRIVE:
            await self.setPermissions(file_id)
        return file_id

    async def copy(self, meta):
        self.setRootNode(Folder(meta))
        await self.traverseFolder(meta.get('id'))
        self.total_bytes = self.size
        newDir = await self.createDirectory(meta.get('name'), Config.GDRIVE_FOLDER_ID)
        await self.copyFolderFromStorage(self.getRootNode().children, newDir)
        self.onTransferComplete()
        return newDir

    async def copyFolderFromStorage(self, storage, parent_id):
        for item in storage:
            if item.mimeType == G_DRIVE_DIR_MIME_TYPE:
                newDir = await self.createDirectory(item.name, parent_id)
                await self.copyFolderFromStorage(item.children, newDir)
            else:
                await self.copyFile(item.id, parent_id)
                self.onProgressUpdate(item.size)

    def traverseStorage(self, storage):
        for item in storage:
            if item.mimeType == G_DRIVE_DIR_MIME_TYPE:
                item.calculateSize(item.children)
                self.traverseStorage(item.children)

    def generateTree(self, storage, prefix=""):
        pointers = [tee] * (len(storage) - 1) + [last]
        for pointer, path in zip(pointers, storage):
            yield f"{prefix}{pointer}{path.name} ({humanbytes(path.size)})"
            if path.mimeType == self.G_DRIVE_DIR_MIME_TYPE:
                extension = branch if pointer == tee else space
                yield from self.generateTree(path.children, prefix=prefix+extension)

    async def retry(self, coro):
        logger.info(f"Sleeping for {self.SLEEP_TIME} and retrying")
        await asyncio.sleep(self.SLEEP_TIME)
        return await coro

    async def getFilesByParentId(self, folder_id, name=None, limit=None):
        files = []
        page_token = None
        if name:
            query = f"'{folder_id}' in parents and (name contains '{name}')"
        else:
            query = f"'{folder_id}' in parents"
        while True:
            resp = await self.service.files.list(supportsAllDrives=True,
                                                 includeTeamDriveItems=True,
                                                 q=query,
                                                 fields='nextPageToken, files(id, name, mimeType, size, iconLink)',
                                                 pageToken=page_token,
                                                 pageSize=500,
                                                 orderBy='folder,name,modifiedTime desc')
            response = await resp.json()
            err = response.get("error", None)
            if err != None and (
                "rate" in err.get("message").lower() or resp.status >= 500
            ):
                return await self.retry(self.getFilesByParentId(folder_id, name, limit))
            for file in response.get('files', []):
                if limit and len(files) == limit:
                    return files
                files.append(file)
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        return files


@bot.on(admin_cmd(pattern="drivesearch ?(.*)", allow_sudo=True))
async def drivesch(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1).strip()
    drive = GDriveHelper()
    await drive.authorize(event)
    files = await drive.getFilesByParentId(Config.GDRIVE_FOLDER_ID, input_str, 20)
    msg = f"**G-Drive Search Query**\n`{input_str}`\n**Results**\n"
    for file in files:
        if file.get("mimeType") == drive.G_DRIVE_DIR_MIME_TYPE:
            msg += "⁍ [{}]({}) (folder)".format(file.get('name'),
                                                drive.formatLink(file.get('id')))+"\n"
        else:
            msg += "⁍ [{}]({}) ({})".format(file.get('name'), drive.formatLink(
                file.get('id'), folder=False), humanbytes(int(file.get('size'))))+"\n"
    await event.edit(msg)


@bot.on(admin_cmd(pattern="gcopy ?(.*)", allow_sudo=True))
async def driveclone(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1).strip()
    mone = await event.reply('Processing..')
    drive = GDriveHelper()
    await drive.authorize(event)
    try:
        fileId = drive.parseLink(input_str)
        meta = await drive.getMetadata(fileId)
    except Exception as e:
        await mone.edit(f"BadLink: {e}")
        return
    link = ""
    if meta.get('mimeType') == G_DRIVE_DIR_MIME_TYPE:
        task1 = drive.copy(meta)
        task2 = progressSpinner(drive, "COPY PROGRESS", mone)
        res = await asyncio.gather(*[task1, task2])
        fileCount = drive.file_count
        size = drive.size
        file_id = res[0]
        link = drive.formatLink(file_id)
    else:
        file_id = await drive.copyFile(meta.get('id'), Config.GDRIVE_FOLDER_ID)
        link = drive.formatLink(file_id, folder=False)
        size = int(meta.get('size') or 0)
        fileCount = 1
    await mone.edit(f"__GDrive Copy:__\n[{meta.get('name')}]({link})\n**Size:** `{humanbytes(size)}`\n**FileCount:** `{fileCount}`")


@bot.on(admin_cmd(pattern="drivedl ?(.*)", allow_sudo=True))
async def gdrivedownload(event):
    if event.fwd_from:
        return
    input_link = event.pattern_match.group(1)
    if not input_link:
        await event.edit("Provide Link kek.")
        return
    mone = await event.reply("Processing...")
    drive = GDriveHelper()
    await drive.authorize(event)
    file_id = drive.parseLink(input_link)
    task = drive.download(file_id, mone)
    task2 = progressSpinner(drive, "DOWNLOAD PROGRESS", mone)
    result = await asyncio.gather(*[task, task2])
    name = result[0]
    await mone.edit(f"Downloaded: `{name}`")


@bot.on(admin_cmd(pattern="drivemeta ?(.*)", allow_sudo=True))
async def gdrivemeta(event):
    if event.fwd_from:
        return
    input_link = event.pattern_match.group(1)
    if not input_link:
        await event.edit("Provide Link kek.")
        return
    mone = await event.reply("Processing...")
    drive = GDriveHelper()
    await drive.authorize(event)
    try:
        file_id = drive.parseLink(input_link)
    except Exception as e:
        await mone.edit(f"Bad Link: {e}")
    msg = ""
    meta = await drive.getMetadata(file_id)
    tree = ""
    await mone.edit("Calculating Size please wait!")
    if meta.get('mimeType') == G_DRIVE_DIR_MIME_TYPE:
        drive.setRootNode(Folder(meta))
        await drive.traverseFolder(file_id)
        drive.getRootNode().calculateSize(drive.getRootNode().children)
        for line in drive.generateTree(drive.getRootNode().children):
            tree += line + "\n"
        size = drive.size
    else:
        size = await drive.getSizeDrive(file_id)
    msg += f"**Name:** `{meta.get('name')}`\n"
    msg += f"**Size:** `{humanbytes(size)}`\n"
    msg += f"**FileCount:** `{drive.file_count}`\n"
    msg += f"**MimeType:** `{meta.get('mimeType')}`\n"
    msg += f"**Trashed:** `{meta.get('trashed')}`\n"
    msg += f"**Description:** `{meta.get('description')}`\n"
    msg += f"**CreatedTime:** `{meta.get('createdTime')}`\n"
    msg += f"**ModifiedTime:** `{meta.get('modifiedTime')}\n`"
    if tree != "":
        msg += f"**Tree:** [here]({await postTextToDogBin(tree)})"
    await mone.edit(msg)


@bot.on(admin_cmd(pattern="gdrive ?(.*)", allow_sudo=True))
async def gdriveupload(event):
    if event.fwd_from:
        return
    mone = await event.reply("Processing ...")
    if Config.G_DRIVE_CLIENT_ID is None or Config.G_DRIVE_CLIENT_SECRET is None:
        await mone.edit("This module requires credentials from https://da.gd/so63O. Aborting!")
        return False
    input_str = event.pattern_match.group(1)
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    required_file_name = None
    start = datetime.now()
    if event.reply_to_msg_id and not input_str:
        reply_message = await event.get_reply_message()
        try:
            c_time = time.time()
            downloaded_file_name = await bot.download_media(
                reply_message,
                Config.TMP_DOWNLOAD_DIRECTORY,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, mone, c_time, "trying to download")
                )
            )
        except Exception as e:  # pylint:disable=C0103,W0703
            await mone.edit(str(e))
            return False
        else:
            end = datetime.now()
            ms = (end - start).seconds
            required_file_name = downloaded_file_name
            await mone.edit("Downloaded to `{}` in {} seconds.".format(downloaded_file_name, ms))
    elif input_str:
        input_str = input_str.strip()
        if os.path.exists(input_str):
            end = datetime.now()
            ms = (end - start).seconds
            required_file_name = input_str
            await mone.edit("Found `{}` in {} seconds.".format(required_file_name, ms))
        else:
            await mone.edit("File Not found in local server. Give me a file path :((")
            return False
    if required_file_name:
        link = ""
        drive = GDriveHelper()
        await drive.authorize(event)
        task = drive.upload(required_file_name, mone)
        task2 = progressSpinner(drive, "UPLOAD PROGRESS", mone)
        result = await asyncio.gather(*[task, task2])
        link = result[0]
        await mone.edit(f"Uploaded To GDrive: [{required_file_name}]({link})")
    else:
        await mone.edit("File Not found in local server. Give me a file path :((")
