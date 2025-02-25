"use client";
import axios from "axios";
import React, { useState } from "react";

export default function Home() {
  const [data, setData] = useState([]);
  const [answer, setAnswer] = useState("");

  const startStreamData = async () => {
    const response = await axios.post("http://localhost:8000/stream-chat", {
      prompt: answer,
      history: data,
    });
    if (!response.ok || !response.body) {
      throw response.statusText;
    }

    const ndata = [
      ...data,
      { role: "user", parts: [{ text: inputRef.current.value }] },
    ];

    const reader = response.body.getReader();
    const txtdecoder = new TextDecoder();
    const loop = true;
    var modelResponse = "";
    while (true) {
      const { value, done } = reader.read();
      if (done) break;
      setAnswer((prev) => {
        prev + value;
      });

      modelResponse += value;
    }

    const updatedData = [
      ...ndata,
      { role: "model", parts: [{ text: modelResponse }] },
    ];
    setData(updatedData)

  };

return (
  <div>
   
  </div>
)
}
