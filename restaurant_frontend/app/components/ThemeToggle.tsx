"use client";

import { useEffect, useState } from "react";

export function ThemeToggle() {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    setIsDark(document.body.classList.contains("dark"));
  }, []);

  const toggleDark = () => {
    if (document.body.classList.contains("dark")) {
      document.body.classList.remove("dark");
      setIsDark(false);
    } else {
      document.body.classList.add("dark");
      setIsDark(true);
    }
  };

  return (
    <button onClick={toggleDark} className="p-2 border rounded fixed top-4 right-4 z-50 bg-white dark:bg-gray-800 dark:text-white shadow">
      {isDark ? "라이트 모드" : "다크 모드"}
    </button>
  );
} 