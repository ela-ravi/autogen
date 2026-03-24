"use client";

import { useCallback, useState } from "react";
import { Upload } from "lucide-react";

const ALLOWED = ["video/mp4", "video/quicktime", "video/x-msvideo", "video/x-matroska", "video/webm"];

interface DropZoneProps {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
}

export function DropZone({ onFileSelect, disabled }: DropZoneProps) {
  const [dragOver, setDragOver] = useState(false);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      if (disabled) return;
      const file = e.dataTransfer.files[0];
      if (file && ALLOWED.includes(file.type)) {
        onFileSelect(file);
      }
    },
    [onFileSelect, disabled]
  );

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onFileSelect(file);
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-12 transition-colors ${
        dragOver ? "border-blue-500 bg-blue-50" : "border-border"
      } ${disabled ? "cursor-not-allowed opacity-50" : "hover:border-blue-400"}`}
    >
      <Upload className="mb-4 h-10 w-10 text-muted-foreground" />
      <p className="mb-2 text-lg font-medium">Drop your video here</p>
      <p className="mb-4 text-sm text-muted-foreground">
        MP4, MOV, AVI, MKV, WebM up to 2GB
      </p>
      <label className="cursor-pointer rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:opacity-90">
        Browse files
        <input
          type="file"
          accept="video/*"
          className="hidden"
          onChange={handleChange}
          disabled={disabled}
        />
      </label>
    </div>
  );
}
