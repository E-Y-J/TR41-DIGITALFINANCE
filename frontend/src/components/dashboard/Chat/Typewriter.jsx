import { useState, useEffect } from "react";
import { Typography } from "@mui/material";

const Typewriter = ({ text, speed = 30 }) => {
  const [displayedText, setDisplayedText] = useState("");

  useEffect(() => {
    let index = 0;
    setDisplayedText("");

    const intervalId = setInterval(() => {
      setDisplayedText(() => text.slice(0, index + 1));
      index++;

      if (index >= text.length) {
        clearInterval(intervalId);
      }
    }, speed);

    return () => clearInterval(intervalId);
  }, [text, speed]);

  return <Typography variant="body2">{displayedText}</Typography>;
};
export default Typewriter;
