#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Media Handler Module
===================

Provides media file processing and management capabilities for the Telegram bot.
Supports image, video, audio, and document handling with optimization and conversion.
"""

import os
import logging
import asyncio
import aiofiles
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from pathlib import Path
import hashlib
import mimetypes
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class MediaInfo:
    """Information about a media file"""
    file_path: str
    file_name: str
    file_size: int
    mime_type: str
    media_type: str  # image, video, audio, document
    duration: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    thumbnail_path: Optional[str] = None
    hash_md5: Optional[str] = None
    created_at: datetime = None

class MediaHandler:
    """
    Advanced media file handler for the Telegram bot.
    
    Features:
    - File type detection and validation
    - Image resizing and optimization
    - Video thumbnail generation
    - Audio file processing
    - File size management
    - Media metadata extraction
    - Thumbnail generation
    - File conversion (basic)
    """
    
    def __init__(self, storage_path: str = "media"):
        self.storage_path = Path(storage_path)
        self.thumbnails_path = self.storage_path / "thumbnails"
        self.temp_path = self.storage_path / "temp"
        
        # Create directories
        self.storage_path.mkdir(exist_ok=True)
        self.thumbnails_path.mkdir(exist_ok=True)
        self.temp_path.mkdir(exist_ok=True)
        
        # Supported file types
        self.supported_images = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        self.supported_videos = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'}
        self.supported_audio = {'.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac'}
        self.supported_documents = {'.pdf', '.doc', '.docx', '.txt', '.zip', '.rar'}
        
        # Size limits (in bytes)
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.max_image_size = 10 * 1024 * 1024  # 10MB
        self.max_video_size = 50 * 1024 * 1024  # 50MB
    
    async def process_file(self, file_path: str, optimize: bool = True) -> Optional[MediaInfo]:
        """
        Process a media file and extract information
        
        Args:
            file_path: Path to the file
            optimize: Whether to optimize the file
            
        Returns:
            Optional[MediaInfo]: Media information or None if processing failed
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None
            
            file_path = Path(file_path)
            file_size = file_path.stat().st_size
            
            # Check file size
            if file_size > self.max_file_size:
                logger.warning(f"File too large: {file_size} bytes")
                return None
            
            # Detect file type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            media_type = self._detect_media_type(file_path.suffix.lower())
            
            if not media_type:
                logger.warning(f"Unsupported file type: {file_path.suffix}")
                return None
            
            # Calculate file hash
            file_hash = await self._calculate_file_hash(str(file_path))
            
            # Create media info
            media_info = MediaInfo(
                file_path=str(file_path),
                file_name=file_path.name,
                file_size=file_size,
                mime_type=mime_type or 'application/octet-stream',
                media_type=media_type,
                hash_md5=file_hash,
                created_at=datetime.now()
            )
            
            # Process based on media type
            if media_type == "image":
                await self._process_image(media_info, optimize)
            elif media_type == "video":
                await self._process_video(media_info, optimize)
            elif media_type == "audio":
                await self._process_audio(media_info)
            elif media_type == "document":
                await self._process_document(media_info)
            
            logger.info(f"✅ Processed {media_type}: {file_path.name}")
            return media_info
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return None
    
    def _detect_media_type(self, file_extension: str) -> Optional[str]:
        """Detect media type from file extension"""
        if file_extension in self.supported_images:
            return "image"
        elif file_extension in self.supported_videos:
            return "video"
        elif file_extension in self.supported_audio:
            return "audio"
        elif file_extension in self.supported_documents:
            return "document"
        return None
    
    async def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of file"""
        try:
            hash_md5 = hashlib.md5()
            async with aiofiles.open(file_path, 'rb') as f:
                async for chunk in self._file_chunks(f):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash: {e}")
            return ""
    
    async def _file_chunks(self, file_object, chunk_size: int = 8192):
        """Async file chunk generator"""
        while True:
            chunk = await file_object.read(chunk_size)
            if not chunk:
                break
            yield chunk
    
    async def _process_image(self, media_info: MediaInfo, optimize: bool):
        """Process image file"""
        try:
            # Try to get image info using PIL if available
            try:
                from PIL import Image
                
                with Image.open(media_info.file_path) as img:
                    media_info.width, media_info.height = img.size
                    
                    # Generate thumbnail
                    await self._generate_image_thumbnail(media_info, img)
                    
                    # Optimize if requested
                    if optimize and media_info.file_size > 2 * 1024 * 1024:  # 2MB
                        await self._optimize_image(media_info, img)
                
            except ImportError:
                logger.warning("PIL not available, skipping image processing")
                
        except Exception as e:
            logger.error(f"Error processing image: {e}")
    
    async def _generate_image_thumbnail(self, media_info: MediaInfo, img=None):
        """Generate thumbnail for image"""
        try:
            if not img:
                from PIL import Image
                img = Image.open(media_info.file_path)
            
            # Create thumbnail
            thumbnail_size = (150, 150)
            img_copy = img.copy()
            img_copy.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
            
            # Save thumbnail
            file_name = Path(media_info.file_name).stem
            thumbnail_path = self.thumbnails_path / f"{file_name}_thumb.jpg"
            
            # Convert to RGB if necessary
            if img_copy.mode in ('RGBA', 'P'):
                rgb_img = Image.new('RGB', img_copy.size, (255, 255, 255))
                rgb_img.paste(img_copy, mask=img_copy.split()[-1] if img_copy.mode == 'RGBA' else None)
                img_copy = rgb_img
            
            img_copy.save(str(thumbnail_path), "JPEG", quality=80)
            media_info.thumbnail_path = str(thumbnail_path)
            
        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")
    
    async def _optimize_image(self, media_info: MediaInfo, img=None):
        """Optimize image file"""
        try:
            if not img:
                from PIL import Image
                img = Image.open(media_info.file_path)
            
            # Resize if too large
            max_width, max_height = 1920, 1080
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Save optimized version
            optimized_path = self.temp_path / f"optimized_{Path(media_info.file_name).name}"
            
            # Convert to RGB if necessary and save with compression
            if img.mode in ('RGBA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            
            img.save(str(optimized_path), "JPEG", quality=85, optimize=True)
            
            # Replace original with optimized version if smaller
            optimized_size = optimized_path.stat().st_size
            if optimized_size < media_info.file_size:
                os.replace(str(optimized_path), media_info.file_path)
                media_info.file_size = optimized_size
                logger.info(f"Image optimized: {media_info.file_size} -> {optimized_size} bytes")
            else:
                optimized_path.unlink()
                
        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
    
    async def _process_video(self, media_info: MediaInfo, optimize: bool):
        """Process video file"""
        try:
            # Try to get video info using moviepy if available
            try:
                import moviepy.editor as mp
                
                with mp.VideoFileClip(media_info.file_path) as video:
                    media_info.duration = int(video.duration) if video.duration else None
                    media_info.width = video.w if hasattr(video, 'w') else None
                    media_info.height = video.h if hasattr(video, 'h') else None
                    
                    # Generate thumbnail from video
                    await self._generate_video_thumbnail(media_info, video)
                
            except ImportError:
                logger.warning("moviepy not available, skipping video processing")
                
        except Exception as e:
            logger.error(f"Error processing video: {e}")
    
    async def _generate_video_thumbnail(self, media_info: MediaInfo, video=None):
        """Generate thumbnail from video"""
        try:
            if not video:
                import moviepy.editor as mp
                video = mp.VideoFileClip(media_info.file_path)
            
            # Extract frame at 1 second or middle of video
            time_pos = min(1.0, video.duration / 2) if video.duration else 1.0
            
            file_name = Path(media_info.file_name).stem
            thumbnail_path = self.thumbnails_path / f"{file_name}_thumb.jpg"
            
            # Extract and save frame
            frame = video.get_frame(time_pos)
            
            # Save using PIL if available
            try:
                from PIL import Image
                img = Image.fromarray(frame)
                img.thumbnail((150, 150), Image.Resampling.LANCZOS)
                img.save(str(thumbnail_path), "JPEG", quality=80)
                media_info.thumbnail_path = str(thumbnail_path)
            except ImportError:
                # Fallback: save frame directly
                import matplotlib.pyplot as plt
                plt.imsave(str(thumbnail_path), frame)
                media_info.thumbnail_path = str(thumbnail_path)
                
        except Exception as e:
            logger.error(f"Error generating video thumbnail: {e}")
    
    async def _process_audio(self, media_info: MediaInfo):
        """Process audio file"""
        try:
            # Try to get audio info using mutagen if available
            try:
                from mutagen import File
                
                audio_file = File(media_info.file_path)
                if audio_file:
                    media_info.duration = int(audio_file.info.length) if hasattr(audio_file.info, 'length') else None
                
            except ImportError:
                logger.warning("mutagen not available, skipping audio metadata extraction")
                
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
    
    async def _process_document(self, media_info: MediaInfo):
        """Process document file"""
        try:
            # For now, just log that it's a document
            # Could add PDF preview generation, etc.
            logger.info(f"Document processed: {media_info.file_name}")
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
    
    async def resize_image(self, 
                          input_path: str, 
                          output_path: str, 
                          max_width: int = 1920, 
                          max_height: int = 1080,
                          quality: int = 85) -> bool:
        """
        Resize image to specified dimensions
        
        Args:
            input_path: Input image path
            output_path: Output image path
            max_width: Maximum width
            max_height: Maximum height
            quality: JPEG quality (1-100)
            
        Returns:
            bool: Success status
        """
        try:
            from PIL import Image
            
            with Image.open(input_path) as img:
                # Calculate new size maintaining aspect ratio
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = rgb_img
                
                # Save resized image
                img.save(output_path, "JPEG", quality=quality, optimize=True)
                
            logger.info(f"Image resized: {input_path} -> {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            return False
    
    async def convert_to_jpeg(self, input_path: str, output_path: str, quality: int = 90) -> bool:
        """
        Convert image to JPEG format
        
        Args:
            input_path: Input image path
            output_path: Output JPEG path
            quality: JPEG quality (1-100)
            
        Returns:
            bool: Success status
        """
        try:
            from PIL import Image
            
            with Image.open(input_path) as img:
                # Convert to RGB
                if img.mode != 'RGB':
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        rgb_img.paste(img, mask=img.split()[-1])
                    else:
                        rgb_img.paste(img)
                    img = rgb_img
                
                # Save as JPEG
                img.save(output_path, "JPEG", quality=quality, optimize=True)
                
            logger.info(f"Image converted to JPEG: {input_path} -> {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error converting to JPEG: {e}")
            return False
    
    def validate_file_size(self, file_path: str, media_type: str = None) -> bool:
        """Validate file size against limits"""
        try:
            file_size = os.path.getsize(file_path)
            
            if media_type == "image":
                return file_size <= self.max_image_size
            elif media_type == "video":
                return file_size <= self.max_video_size
            else:
                return file_size <= self.max_file_size
                
        except Exception:
            return False
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get list of supported file formats"""
        return {
            "images": list(self.supported_images),
            "videos": list(self.supported_videos),
            "audio": list(self.supported_audio),
            "documents": list(self.supported_documents)
        }
    
    async def cleanup_temp_files(self, max_age_hours: int = 24):
        """Clean up temporary files older than specified age"""
        try:
            from datetime import datetime, timedelta
            
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
            for file_path in self.temp_path.glob('*'):
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_time:
                        file_path.unlink()
                        logger.info(f"Cleaned up temp file: {file_path.name}")
                        
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")
    
    def get_media_stats(self) -> Dict[str, Any]:
        """Get media storage statistics"""
        try:
            total_files = 0
            total_size = 0
            
            for file_path in self.storage_path.rglob('*'):
                if file_path.is_file():
                    total_files += 1
                    total_size += file_path.stat().st_size
            
            return {
                "total_files": total_files,
                "total_size": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "storage_path": str(self.storage_path)
            }
            
        except Exception as e:
            logger.error(f"Error getting media stats: {e}")
            return {}

# Global media handler instance
media_handler = MediaHandler()

__all__ = ['MediaHandler', 'MediaInfo', 'media_handler']