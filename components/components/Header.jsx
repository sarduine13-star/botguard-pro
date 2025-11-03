import React from "react";
import flag from "../assets/usflag.png"; // optional image if you add one later

export default function Header() {
  return (
    <header className="flex justify-between items-center px-6 py-4 border-b border-gray-800 bg-black bg-opacity-80">
      <h1 className="text-2xl font-extrabold text-primary tracking-wider">
        BOTGUARD <span className="text-accent">PRO</span>
      </h1>
      <div className="flex items-center gap-3">
        <span className="text-sm text-gray-400 hidden sm:block">
          24/7 U.S. Protection
        </span>
        <img
          src={flag}
          alt="U.S. Flag"
          className="w-10 h-6 object-cover border border-gray-700"
        />
      </div>
    </header>
  );
}
