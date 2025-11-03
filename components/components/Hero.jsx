import React from "react";
import { motion } from "framer-motion";
import { loadStripe } from "@stripe/stripe-js";

const stripePromise = loadStripe("pk_test_yourPublishableKeyHere");

export default function Hero() {
  const handleCheckout = async (priceId) => {
    const stripe = await stripePromise;
    stripe.redirectToCheckout({
      lineItems: [{ price: priceId, quantity: 1 }],
      mode: "subscription",
      successUrl: window.location.origin + "/success",
      cancelUrl: window.location.origin + "/cancel",
    });
  };

  return (
    <section className="text-center py-20 bg-gradient-to-b from-black via-gray-900 to-black">
      <motion.h2
        initial={{ opacity: 0, y: -40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-6xl font-bold hero-text mb-4"
      >
        Get Your Time Back
      </motion.h2>
      <p className="text-gray-400 text-lg mb-8">
        Stop fighting bots and downtime — BotGuard Pro runs 24/7 so you don’t have to.
      </p>
      <button
        onClick={() => handleCheckout("price_placeholder")}
        className="btn text-lg shadow-xl"
      >
        Start 7-Day Free Trial
      </button>
    </section>
  );
}
