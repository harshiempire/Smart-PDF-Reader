"use client";
import React, { useState } from "react";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [userId, setUserId] = useState("demo_user");
  const [result, setResult] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    setUploading(true);
    try {
      const res = await fetch(
        `http://localhost:8000/process-pdf?user_id=${encodeURIComponent(userId)}`,
        {
          method: "POST",
          body: formData,
        }
      );
      if (!res.ok) throw new Error("Upload failed");
      const data = await res.json();
      setResult(data.document_id);
    } catch (err) {
      console.error(err);
      setResult("error");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-4 space-y-4">
      <form onSubmit={handleSubmit} className="space-y-2">
        <input
          type="text"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          placeholder="User ID"
          className="border p-2"
        />
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
        />
        <button
          type="submit"
          disabled={!file || uploading}
          className="border px-3 py-1"
        >
          {uploading ? "Uploading..." : "Upload"}
        </button>
      </form>
      {result && <div>Document ID: {result}</div>}
    </div>
  );
}
