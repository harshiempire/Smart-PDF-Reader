import { useState, useEffect } from "react";

const StreamResponseEventSource = ({ input }: { input: string }) => {
  const [answer, setAnswer] = useState("");
  const [startStream, setStartStream] = useState(false);

  useEffect(() => {
    if (startStream) {
      setAnswer("");
      const eventSource = new EventSource(
        `http://localhost:8000/stream-with-get?question=${input}`
      );

      eventSource.onmessage = function (event) {
        console.log(event);
        setAnswer((prevAnswer) => prevAnswer + event.data);
      };

      eventSource.onerror = function (err) {
        console.error("EventSource failed.");
        console.error(err);
        eventSource.close();
      };

      return () => {
        setStartStream(false);
        eventSource.close();
      };
    }
  }, [startStream, input]);
};

export default StreamResponseEventSource;
