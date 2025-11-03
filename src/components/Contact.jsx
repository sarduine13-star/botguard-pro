import React, { useState } from "react";

export default function Contact() {
  const [sent, setSent] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", message: "" });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSent(true);
  };

  return (
    <section className="py-20 bg-black text-center" id="contact">
      <h3 className="text-4xl font-bold mb-10">Contact Us</h3>
      {!sent ? (
        <form
          onSubmit={handleSubmit}
          className="max-w-lg mx-auto space-y-4 text-left"
        >
          <input
            name="name"
            placeholder="Your Name"
            value={form.name}
            onChange={handleChange}
            required
          />
          <input
            name="email"
            type="email"
            placeholder="Email Address"
            value={form.email}
            onChange={handleChange}
            required
          />
          <textarea
            name="message"
            rows="4"
            placeholder="Message"
            value={form.message}
            onChange={handleChange}
          />
          <button type="submit" className="btn w-full">Send Message</button>
        </form>
      ) : (
        <p className="text-primary text-lg mt-6">
          Thank you! We’ll be in touch soon.
        </p>
      )}
    </section>
  );
}
