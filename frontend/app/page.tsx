"use client";
import axios from "axios";
import React, { useRef, useState } from "react";

export default function Home() {
  const inputRef = useRef(null);
  const [data, setData] = useState([]);
  const [answer, setAnswer] = useState("");
  const [streamdiv, setStreamdiv] = useState(false);

  const startStreamData = async () => {
    try {
      let ndata = [
        ...data,
        { role: "user", parts: [{ text: inputRef.current.value }] },
      ];

      var modelResponse = "";

      const chatData = {
        prompt: inputRef.current.value,
        history: ndata,
      };

      setData(ndata);
      inputRef.current.value = "";
      inputRef.current.placeholder = "Waiting for model response";

      const response = await axios.post(
        "http://localhost:8000/stream-chat",
        chatData
      );
      if (!response.ok || !response.body) {
        throw response.statusText;
      }

      ndata = [
        ...data,
        { role: "user", parts: [{ text: inputRef.current.value }] },
      ];

      setStreamdiv(true);
      const reader = response.body.getReader();
      const txtdecoder = new TextDecoder();
      while (true) {
        const { value, done } = reader.read();
        if (done) break;
        const decodedTxt = txtdecoder.decode(value, { stream: true });
        setAnswer((prev) => {
          prev + decodedTxt;
        });

        modelResponse += value;
      }

      setData(updatedData);
    } catch (err) {
      modelResponse = "Error occurred";
    } finally {
      const updatedData = [
        ...data,
        { role: "model", parts: [{ text: modelResponse }] },
      ];

      inputRef.current.placeholder = "Next messages";
      setData(updatedData);
      setAnswer("");
      setStreamdiv(false);
    }
  };

  return (
    <div className="grid grid-flow-col grid-rows-3 gap-4 h-screen">
      <div className="border row-span-3 ">01</div>
      <div className="border col-span-2 row-span-2">
        {data.map((msg, index) => {
          return (
            <div key={index}>
              <div>{msg.role}</div>
              <div>{msg.parts[0].text}</div>
            </div>
          );
        })}
        {streamdiv && <div>{answer}</div>}
      </div>
      <div className="border col-span-2 ">
        <input ref={inputRef} />
        <button onClick={startStreamData}>send</button>
      </div>
    </div>
  );
}
