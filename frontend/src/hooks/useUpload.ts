"use client";

import { useCallback, useState } from "react";
import Cookies from "js-cookie";
import type { UploadResponse } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

export function useUpload() {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const uploadVideo = useCallback(async (file: File): Promise<UploadResponse> => {
    setUploading(true);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append("file", file);

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open("POST", `${API_URL}/api/v1/uploads/video`);

      const token = Cookies.get("access_token");
      if (token) {
        xhr.setRequestHeader("Authorization", `Bearer ${token}`);
      }

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          setUploadProgress(Math.round((event.loaded / event.total) * 100));
        }
      };

      xhr.onload = () => {
        setUploading(false);
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(JSON.parse(xhr.responseText));
        } else {
          reject(new Error(xhr.responseText));
        }
      };

      xhr.onerror = () => {
        setUploading(false);
        reject(new Error("Upload failed"));
      };

      xhr.send(formData);
    });
  }, []);

  return { uploading, uploadProgress, uploadVideo };
}
