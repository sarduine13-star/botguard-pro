import React, { useState, useEffect } from "react";

export default function SpinWheel() {
  const [showWheel, setShowWheel] = useState(false);
  const [result, setResult] = useState("");

  useEffect(() => {
    const timer = setTimeout(() => setShowWheel(true), 3000);
    return () => clearTimeout(timer);
  }, []);

  const prizes = [
    "1 Month Free",
    "50% Off First Month",
    "10% Off",
    "Try Again"
  ];

  const spin = () => {
    const randomIndex = Math.floor(Math.random() * prizes.length);
    setResult(prizes[randomIndex]);
  };

  if (!showWheel) return null;

  return (
    <div className="wheel-overlay">
      <div className="wheel-container">
        <h3 className="text-2xl font-bold mb-4 text-primary">Spin the Shield!</h3>
        <p className="text-gray-400 mb-4">Win discounts or even your first month free.</p>
        <button onClick={spin} className="btn mb-4">Spin</button>
        {result && (
          <div className="mt-2 text-xl font-semibold text-neon">
            {result === "Try Again"
              ? "No luck this time, but your site stays safe!"
              : `You won: ${result}!`}
          </div>
        )}
        <button
          onClick={() => setShowWheel(false)}
          className="mt-6 text-gray-400 underline hover:text-primary"
        >
          Close
        </button>
      </div>
    </div>
  );
}
