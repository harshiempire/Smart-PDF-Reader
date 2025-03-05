"use client";
import React, { useRef, useState } from "react";
import Markdown from "react-markdown";

export default function Home() {
  const handleKeypress = (e: any) => {
    if (e.keyCode === 13 && !e.shiftKey) {
      startStreamData();
      e.preventDefault();
    }
  };

  const { textAreaRef, resizeTextArea } = useAutoResizeTextArea();
  const [data, setData] = useState([]);
  const [answer, setAnswer] = useState("");
  const [streamdiv, setStreamdiv] = useState(false);

  const startStreamData = async () => {
    let ndata = [
      ...data,
      { role: "user", parts: [{ text: textAreaRef.current.value }] },
    ];

    let modelResponse = "";
    try {
      const chatData = {
        chat: textAreaRef.current.value,
        history: ndata,
      };

      setData(ndata);
      textAreaRef.current.value = "";
      resizeTextArea();
      textAreaRef.current.placeholder = "Waiting for model response";

      executeScroll();

      const response = await fetch("http://localhost:8000/stream-chat", {
        method: "POST",
        headers: {
          Accept: "application/json, text/plain, */*",
          "Content-Type": "application/json",
        },
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
        setAnswer((prev) => prev + decodedTxt);
        modelResponse += decodedTxt;
        executeScroll();
      }
    } catch (err) {
      modelResponse = "Error occurred";
      console.error(err);
    } finally {
      setStreamdiv(false);
      textAreaRef.current.placeholder = "Next messages";
      setData([...ndata, { role: "model", parts: [{ text: modelResponse }] }]);
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
    <div className="flex h-screen">
      {/* Sidebar for Chat List */}
      <div className="h-full w-1/2 border border-gray-500 flex-shrink-0">
        Side Bar for chat list
      </div>

      {/* Chat Box */}
      <div className="relative flex flex-col h-full w-1/2 border border-gray-500">
        {/* Chat Messages */}
        <div className="overflow-y-auto flex-grow border border-gray-900 pb-24">
          {data.map((msg, index) => (
            <div key={index}>
              <div>{msg.role}</div>
              <div className="p-3">
                <Markdown>{msg.parts[0].text}</Markdown>
              </div>
            </div>
          ))}
          {streamdiv && (
            <>
              <div>model</div>
              <div className="p-3">
                <Markdown>{answer}</Markdown>
              </div>
            </>
          )}
          <span id="checkpoint"></span>
        </div>

        {/* Input Box - Now Sticky for Better UX */}
        <div className="sticky bottom-0 left-0 w-full bg-white dark:bg-gray-900 border-t border-gray-900 p-3">
          <textarea
            className="m-0 w-full resize-none border-0 bg-transparent p-0 pr-7 focus:ring-0 dark:bg-transparent pl-2 md:pl-0"
            ref={textAreaRef}
            onInput={resizeTextArea}
            placeholder="Send a message..."
            onKeyDown={handleKeypress}
            style={{
              height: "24px",
              maxHeight: "200px",
              overflowY: "hidden",
            }}
          />
        </div>
      </div>
    </div>
  );
}

function useAutoResizeTextArea() {
  const textAreaRef = useRef<HTMLTextAreaElement>(null);

  const resizeTextArea = () => {
    if (textAreaRef.current) {
      textAreaRef.current.style.height = "auto"; // Reset height
      textAreaRef.current.style.height = `${textAreaRef.current.scrollHeight}px`; // Set new height
    }
  };

  return { textAreaRef, resizeTextArea };
}
