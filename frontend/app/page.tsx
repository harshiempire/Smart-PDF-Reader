"use client";
import React, { useRef, useState } from "react";

export default function Home() {
  const inputRef = useRef(null);
  const [data, setData] = useState([]);
  const [answer, setAnswer] = useState("");
  const [streamdiv, setStreamdiv] = useState(false);

  const startStreamData = async () => {
    let ndata = [
      ...data,
      { role: "user", parts: [{ text: inputRef.current.value }] },
    ];

    let modelResponse = "";
    try {
      const chatData = {
        chat: inputRef.current.value,
        history: ndata,
      };

      setData(ndata);
      inputRef.current.value = "";
      inputRef.current.placeholder = "Waiting for model response";

      // console.log("hi 1");

      let headerConfig = {
        Accept: "application/json, text/plain, */*",
        "Content-Type": "application/json",
      };
      setAnswer("");
      const response = await fetch("http://localhost:8000/stream-chat", {
        method: "post",
        headers: headerConfig,
        body: JSON.stringify(chatData),
      });

      if (!response.ok || !response.body) {
        throw response.statusText;
      }


      setStreamdiv(true);
      const reader = response.body.getReader();
      const txtdecoder = new TextDecoder();
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const decodedTxt = txtdecoder.decode(value, { stream: true });
        setAnswer((prev) => {
          return prev + decodedTxt;
        });

        modelResponse += decodedTxt;
      }

    } catch (err) {
      modelResponse = "Error occurred";
    } finally {
      const updatedData = [
        ...ndata,
        { role: "model", parts: [{ text: modelResponse }] },
      ];

      setStreamdiv(false);
      inputRef.current.placeholder = "Next messages";
      setData(updatedData);
      setAnswer("");
    }
  };

  return (
    <div className="container m-auto grid grid-cols-3 gap-4 md:grid-cols-5 lg:grid-cols-8 ">
      <div className="tile col-start-1 col-end-4 bg-teal-500 md:col-start-1 md:col-end-6 lg:col-start-1 lg:col-end-9">01</div>
      <div className="h-screen tile col-span-1 border md:col-span-2 lg:col-span-3">02</div>
      <div className="tile col-span-2 border md:col-span-3 lg:col-span-5">
        <div className="">
          {data.map((msg, index) => {
            return (
              <div key={index}>
                
                <div className="">{msg.role}</div>
                <div>{msg.parts[0].text}</div>
              </div>
            );
          })}
          {streamdiv && <div>{answer}</div>}
        </div>
        <div className="">
          <input className="font-black" ref={inputRef} />
          <button onClick={startStreamData}>send</button>
        </div>
      </div>
    </div>
  );
}
