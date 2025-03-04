"use client";
import React, { useEffect, useRef, useState } from "react";
import Markdown from "react-markdown";

export default function Home() {
  const handleKeypress = (e: any) => {
    // It's triggers by pressing the enter key
    if (e.keyCode == 13 && !e.shiftKey) {
      startStreamData();
      e.preventDefault();
    }
  };
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [showEmptyChat, setShowEmptyChat] = useState(true);
  const [conversation, setConversation] = useState<any[]>([]);
  const [message, setMessage] = useState("");
const { textAreaRef, resizeTextArea } = useAutoResizeTextArea();


  const inputRef = useRef(null);
  const [data, setData] = useState([]);
  const [answer, setAnswer] = useState("");
  const [streamdiv, setStreamdiv] = useState(false);
  useEffect(() => {
    if (textAreaRef.current) {
      textAreaRef.current.style.height = "24px";
      textAreaRef.current.style.height = `${textAreaRef.current.scrollHeight}px`;
    }
  }, [answer, textAreaRef]);
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
      textAreaRef.current.placeholder = "Waiting for model response";

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
      textAreaRef.current.placeholder = "Next messages";
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
    <div className="flex h-screen">
      <div className="sidebar m-0 h-full w-1/2 border border-gray-500">
        Side Bar for chat list
      </div>
      <div className="overflow-y-auto justify- m-0 flex h-full w-1/2 flex-col border border-gray-500">
        <div className="overflow-y-auto messages flex-grow border border-gray-900">
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
            <>
              {"model"}
              <div className="p-3">
                <Markdown>{answer}</Markdown>
              </div>
            </>
          )}
          <span className="my-9" id="checkpoint"></span>
        </div>
        <div className="inputmessage h-20 border border-gray-900">
          <textarea
            className="m-0 w-full resize-none border-0 bg-transparent p-0 pr-7 focus:ring-0 focus-visible:ring-0 dark:bg-transparent pl-2 md:pl-0"
            ref={textAreaRef}
            onInput={resizeTextArea}  // This ensures height updates dynamically

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
      textAreaRef.current.style.height = "auto"; // Reset height first
      textAreaRef.current.style.height = `${textAreaRef.current.scrollHeight}px`; // Set new height
    }
  };

  useEffect(() => {
    resizeTextArea();
  }, []);

  return { textAreaRef, resizeTextArea };
}

