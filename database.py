import motor.motor_asyncio
from config import Config
import logging  # Added for logging errors and important information
from .utils import send_log


class Database:
    def __init__(self, uri, database_name):
        # Never raise during module import: one missing database variable must not
        # prevent unrelated commands such as /help and /tutorial from loading.
        self.is_configured = bool(uri and str(uri).strip())
        self._client = (
            motor.motor_asyncio.AsyncIOMotorClient(
                str(uri).strip(), serverSelectionTimeoutMS=10000
            )
            if self.is_configured else None
        )
        self.AshutoshGoswami24 = self._client[database_name] if self._client else None
        self.col = self.AshutoshGoswami24.user if self.AshutoshGoswami24 else None

    def require_database(self):
        if not self.is_configured or self.col is None:
            raise RuntimeError(
                "Database is not configured. Add DB_URL to the Render environment variables."
            )

    def new_user(self, id):
        return dict(
            _id=int(id),
            file_id=None,
            caption=None,
            metadata=True,
            metadata_code="Telegram : @ANIFLIXANIMETAMIL",
            metadata_title=None,
            metadata_author=None,
            metadata_artist=None,
            metadata_audio=None,
            metadata_subtitle=None,
            metadata_video=None,
            format_template=None,
        )

    async def add_user(self, b, m):
        u = m.from_user
        if not await self.is_user_exist(u.id):
            user = self.new_user(u.id)
            try:
                await self.col.insert_one(user)
                await send_log(b, u)
            except Exception as e:
                logging.error(f"Error adding user {u.id}: {e}")

    async def is_user_exist(self, id):
        try:
            user = await self.col.find_one({"_id": int(id)})
            return bool(user)
        except Exception as e:
            logging.error(f"Error checking if user {id} exists: {e}")
            return False

    async def total_users_count(self):
        try:
            count = await self.col.count_documents({})
            return count
        except Exception as e:
            logging.error(f"Error counting users: {e}")
            return 0

    async def get_all_users(self):
        try:
            all_users = self.col.find({})
            return all_users
        except Exception as e:
            logging.error(f"Error getting all users: {e}")
            return None

    async def delete_user(self, user_id):
        try:
            await self.col.delete_many({"_id": int(user_id)})
        except Exception as e:
            logging.error(f"Error deleting user {user_id}: {e}")

    async def set_thumbnail(self, id, file_id):
        try:
            await self.col.update_one({"_id": int(id)}, {"$set": {"file_id": file_id}})
        except Exception as e:
            logging.error(f"Error setting thumbnail for user {id}: {e}")

    async def get_thumbnail(self, id):
        try:
            user = await self.col.find_one({"_id": int(id)})
            return user.get("file_id", None) if user else None
        except Exception as e:
            logging.error(f"Error getting thumbnail for user {id}: {e}")
            return None

    async def set_caption(self, id, caption):
        try:
            await self.col.update_one({"_id": int(id)}, {"$set": {"caption": caption}})
        except Exception as e:
            logging.error(f"Error setting caption for user {id}: {e}")

    async def get_caption(self, id):
        try:
            user = await self.col.find_one({"_id": int(id)})
            return user.get("caption", None) if user else None
        except Exception as e:
            logging.error(f"Error getting caption for user {id}: {e}")
            return None

    async def set_format_template(self, id, format_template):
        try:
            await self.col.update_one(
                {"_id": int(id)}, {"$set": {"format_template": format_template}}
            )
        except Exception as e:
            logging.error(f"Error setting format template for user {id}: {e}")

    async def get_format_template(self, id):
        try:
            user = await self.col.find_one({"_id": int(id)})
            return user.get("format_template", None) if user else None
        except Exception as e:
            logging.error(f"Error getting format template for user {id}: {e}")
            return None

    async def set_media_preference(self, id, media_type):
        try:
            await self.col.update_one(
                {"_id": int(id)}, {"$set": {"media_type": media_type}}
            )
        except Exception as e:
            logging.error(f"Error setting media preference for user {id}: {e}")

    async def get_media_preference(self, id):
        try:
            user = await self.col.find_one({"_id": int(id)})
            return user.get("media_type", None) if user else None
        except Exception as e:
            logging.error(f"Error getting media preference for user {id}: {e}")
            return None

    async def set_metadata(self, id, bool_meta):
        try:
            await self.col.update_one(
                {"_id": int(id)}, {"$set": {"metadata": bool_meta}}
            )
        except Exception as e:
            logging.error(f"Error setting metadata for user {id}: {e}")

    async def get_metadata(self, id):
        try:
            user = await self.col.find_one({"_id": int(id)})
            return user.get("metadata", None) if user else None
        except Exception as e:
            logging.error(f"Error getting metadata for user {id}: {e}")
            return None

    async def set_metadata_code(self, id, metadata_code):
        try:
            await self.col.update_one(
                {"_id": int(id)}, {"$set": {"metadata_code": metadata_code}}
            )
        except Exception as e:
            logging.error(f"Error setting metadata code for user {id}: {e}")

    async def get_metadata_code(self, id):
        try:
            user = await self.col.find_one({"_id": int(id)})
            return user.get("metadata_code", None) if user else None
        except Exception as e:
            logging.error(f"Error getting metadata code for user {id}: {e}")
            return None

    async def _set_metadata_field(self, id, field, value):
        try:
            await self.col.update_one({"_id": int(id)}, {"$set": {field: value}}, upsert=False)
        except Exception as e:
            logging.error(f"Error setting {field} for user {id}: {e}")

    async def _get_metadata_field(self, id, field):
        try:
            user = await self.col.find_one({"_id": int(id)})
            return user.get(field) if user else None
        except Exception as e:
            logging.error(f"Error getting {field} for user {id}: {e}")
            return None

    async def set_title(self, id, title):
        await self._set_metadata_field(id, "metadata_title", title)

    async def get_title(self, id):
        return await self._get_metadata_field(id, "metadata_title")

    async def set_author(self, id, author):
        await self._set_metadata_field(id, "metadata_author", author)

    async def get_author(self, id):
        return await self._get_metadata_field(id, "metadata_author")

    async def set_artist(self, id, artist):
        await self._set_metadata_field(id, "metadata_artist", artist)

    async def get_artist(self, id):
        return await self._get_metadata_field(id, "metadata_artist")

    async def set_audio(self, id, audio):
        await self._set_metadata_field(id, "metadata_audio", audio)

    async def get_audio(self, id):
        return await self._get_metadata_field(id, "metadata_audio")

    async def set_subtitle(self, id, subtitle):
        await self._set_metadata_field(id, "metadata_subtitle", subtitle)

    async def get_subtitle(self, id):
        return await self._get_metadata_field(id, "metadata_subtitle")

    async def set_video(self, id, video):
        await self._set_metadata_field(id, "metadata_video", video)

    async def get_video(self, id):
        return await self._get_metadata_field(id, "metadata_video")


AshutoshGoswami24 = Database(Config.DB_URL, Config.DB_NAME)
