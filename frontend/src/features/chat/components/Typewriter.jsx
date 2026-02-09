import { useState, useEffect, memo } from "react";
import { Typography } from "@mui/material";

const Typewriter = memo(({ text, speed = 15, onComplete }) => {
  const [displayedText, setDisplayedText] = useState("");

  useEffect(() => {
    console.log("⌨️ Typewriter: Animation Started");
    let index = 0;
    setDisplayedText("");

    const intervalId = setInterval(() => {
      setDisplayedText(text.slice(0, index + 1));
      index++;

      if (index >= text.length) {
        clearInterval(intervalId);
        console.log("⌨️ Typewriter: Animation Finished");

        if (onComplete) onComplete();
      }
    }, speed);

    return () => clearInterval(intervalId);
  }, [text, speed, onComplete]);

  return (
    <Typography
      variant="body2"
      sx={{
        fontWeight: 500,
        lineHeight: 1.5,
        whiteSpace: "pre-wrap",
        wordBreak: "break-word",
      }}
    >
      {displayedText}

      {displayedText.length < text.length && " ▎"}
    </Typography>
  );
});

export default Typewriter;
