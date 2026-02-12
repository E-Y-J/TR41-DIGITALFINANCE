import { useState, useEffect } from "react";
import FormattedMessage from "../../../components/common/FormattedMessage";

/**
 * Typewriter - Animated text reveal with formatting support
 *
 * Animates text character by character, then renders with full formatting
 * once complete. Supports markdown-like formatting in AI responses.
 */
const Typewriter = ({ text, speed = 30 }) => {
  const [displayedText, setDisplayedText] = useState("");
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    let index = 0;
    setDisplayedText("");
    setIsComplete(false);

    const intervalId = setInterval(() => {
      setDisplayedText(text.slice(0, index + 1));
      index++;

      if (index >= text.length) {
        clearInterval(intervalId);
        setIsComplete(true);
      }
    }, speed);

    return () => clearInterval(intervalId);
  }, [text, speed]);

  // Use FormattedMessage once typing is complete for proper formatting
  // During typing, show plain text to avoid formatting flicker
  if (isComplete) {
    return <FormattedMessage text={displayedText} />;
  }

  return <FormattedMessage text={displayedText} />;
};

export default Typewriter;
