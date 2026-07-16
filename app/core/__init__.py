# from pydantic_settings import BaseSettings
# from functools import lru_cache


# class Settings(BaseSettings):
#     # database
#     SUPABASE_URL: str

#     # auth
#     SECRET_KEY: str
#     ALGORITHM: str = "HS256"
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

#     # huggingface
#     HF_TOKEN: str

#     # jina
#     JINA_API_KEY: str

#     # aws s3
#     AWS_ACCESS_KEY_ID: str
#     AWS_SECRET_ACCESS_KEY: str
#     AWS_REGION: str = "ap-south-1"
#     S3_BUCKET_NAME: str

#     # redis
#     REDIS_URL: str = "redis://localhost:6379/0"

#     # app
#     APP_ENV: str = "development"    # development | production
#     APP_NAME: str = "RAG Document Analyzer"
#     APP_VERSION: str = "1.0.0"

#     class Config:
#         env_file = ".env"
#         extra = "ignore"   # ignore extra fields in .env


# @lru_cache()
# def get_settings() -> Settings:
#     return Settings()


# settings = get_settings()