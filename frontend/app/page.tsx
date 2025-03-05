"use client";
import React, { useRef, useState } from "react";
import Markdown from "react-markdown";

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
      executeScroll();

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
        executeScroll();
      }
    } catch (err) {
      modelResponse = "Error occurred";
      console.error(err);
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

  function executeScroll() {
    const element = document.getElementById("checkpoint");
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  }
  return (
    <div className="px-5 m-auto grid grid-cols-3 gap-4 md:grid-cols-5 lg:grid-cols-8 ">
      <div className="overflow-y-scroll h-screen tile col-span-1 border md:col-span-2 lg:col-span-3">
        02
      </div>
      <div className=" overflow-y-scroll h-screen tile col-span-2 border md:col-span-3 lg:col-span-5">
        <div className="messages w-full">
          {data.map((msg, index) => {
            return (
              <div key={index}>
                <div className="">{msg.role}</div>
                <div className="p-3">
                  <Markdown>{msg.parts[0].text}</Markdown>
                </div>
              </div>
            );
          })}
          {streamdiv && (
            <div className="p-3">
              <Markdown>{answer}</Markdown>
            </div>
          )}
          <span id="checkpoint"></span>
        </div>
        <div className="">
          <input className="text-black" ref={inputRef} />
          <button onClick={startStreamData}>send</button>
        </div>
      </div>
    </div>
  );
}
