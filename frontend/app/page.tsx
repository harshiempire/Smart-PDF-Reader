"use client";
import axios from "axios";
import React, { useRef, useState } from "react";

export default function Home() {
  const inputRef = useRef(null);
  const [data, setData] = useState([]);
  const [answer, setAnswer] = useState("");
  const [streamdiv, setStreamdiv] = useState(false);

  const startStreamData = async () => {
    const ndata = [
      ...data,
      { role: "user", parts: [{ text: inputRef.current.value }] },
    ];

      let modelResponse = "";

      const chatData = {
        prompt: inputRef.current.value,
        history: 
      }

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

      const ndata = [
        ...data,
        { role: "user", parts: [{ text: inputRef.current.value }] },
      ];

      const reader = response.body.getReader();
      const txtdecoder = new TextDecoder();
      while (true) {
        const { value, done } = reader.read();
        if (done) break;
        setAnswer((prev) => {
          prev + value;
        });

        modelResponse += value;
      }

      setData(updatedData);
    } catch (err) {
      modelResponse = "Error occurred";
    } finally {
      const updatedData = [
        ...ndata,
        { role: "model", parts: [{ text: modelResponse }] },
      ];
      setAnswer("");
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
        <button onClick={startStreamData}></button>
      </div>
    </div>
  );
}
