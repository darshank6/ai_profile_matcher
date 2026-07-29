import os
import uuid

from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import status

from app.repositories.resume_repo import ResumeRepository
from app.utils.file_parser import extract_text_from_file


class ResumeService:
    def __init__(self, db):
        self.resume_repo = ResumeRepository(db)

    async def upload_resume(
        self,
        user_id: int,
        file: UploadFile
    ):
        allowed_extensions = [
            ".pdf",
            ".docx",
            ".txt"
        ]

        max_file_size = 5 * 1024 * 1024

        original_filename = file.filename

        if not original_filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File name is missing"
            )

        file_extension = os.path.splitext(
            original_filename
        )[1].lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF, DOCX and TXT files are allowed"
            )

        file_content = await file.read()

        file_size = len(file_content)

        if file_size > max_file_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size should not exceed 5 MB"
            )

        upload_folder = os.path.join(
            "uploads",
            "resumes"
        )

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        unique_filename = (
            f"{uuid.uuid4()}{file_extension}"
        )

        file_path = os.path.join(
            upload_folder,
            unique_filename
        )

        with open(
            file_path,
            "wb"
        ) as saved_file:
            saved_file.write(file_content)

        extracted_text = extract_text_from_file(
            file_path=file_path,
            file_extension=file_extension
        )

        resume_data = {
            "user_id": user_id,
            "original_filename": original_filename,
            "stored_filename": unique_filename,
            "file_path": file_path,
            "file_type": file_extension,
            "file_size": file_size,
            "extracted_text": extracted_text
        }

        resume = self.resume_repo.create_resume(
            resume_data
        )

        return resume

    def get_my_resumes(
        self,
        user_id: int,
        skip: int,
        limit: int
    ):
        return self.resume_repo.get_user_resumes(
            user_id=user_id,
            skip=skip,
            limit=limit
        )

    def get_resume(
        self,
        resume_id: int,
        user_id: int
    ):
        resume = self.resume_repo.get_resume_by_id(
            resume_id=resume_id,
            user_id=user_id
        )

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )

        return resume

    def delete_resume(
        self,
        resume_id: int,
        user_id: int
    ):
        resume = self.resume_repo.get_resume_by_id(
            resume_id=resume_id,
            user_id=user_id
        )

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )

        if os.path.exists(resume.file_path):
            os.remove(resume.file_path)

        self.resume_repo.delete_resume(
            resume
        )

        return {
            "message": "Resume deleted successfully"
        }