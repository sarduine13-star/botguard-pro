import React from "react";

export default function Footer() {
  return (
    <footer className="text-center py-10 border-t border-gray-800 bg-black">
      <p className="text-gray-400 text-sm mb-2">
        © {new Date().getFullYear()} BotGuard Pro. All Rights Reserved.
      </p>
      <p className="text-gray-500 text-xs">
        Powered by <span className="text-primary font-semibold">Redwine Innovations</span>
      </p>
      <div className="mt-4 space-x-4 text-gray-400">
        <a href="/privacy" className="hover:text-primary">Privacy Policy</a>
        <a href="/cookies" className="hover:text-primary">Cookies</a>
      </div>
    </footer>
  );
}
