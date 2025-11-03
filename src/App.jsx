import React from "react";
import Header from "./components/Header";
import Hero from "./components/Hero";
import Counter from "./components/Counter";
import Pricing from "./components/Pricing";
import Contact from "./components/Contact";
import Footer from "./components/Footer";
import SpinWheel from "./components/SpinWheel";

export default function App() {
  return (
    <main className="min-h-screen bg-dark text-white font-sans">
      <Header />
      <Hero />
      <Counter />
      <Pricing />
      <SpinWheel />
      <Contact />
      <Footer />
    </main>
  );
}
