import React from "react";

const tiers = [
  {
    name: "Pay-As-You-Go",
    price: "$9.99/mo + usage",
    features: ["100K requests", "Upgrade anytime", "Cancel anytime"],
    stripeId: "price_placeholder1",
  },
  {
    name: "Pro",
    price: "$39/mo",
    features: ["Analytics", "Add-ons", "Priority Support"],
    stripeId: "price_placeholder2",
  },
  {
    name: "AI Pro",
    price: "$99/mo",
    features: ["AI Firewall", "Threat Intel", "Priority SLA"],
    stripeId: "price_placeholder3",
  },
  {
    name: "Lifetime",
    price: "$375 one-time",
    features: ["Permanent License", "Updates Forever"],
    stripeId: "price_placeholder4",
  },
];

export default function Pricing() {
  const handleClick = (id) => {
    window.alert("Stripe Checkout placeholder for " + id);
  };

  return (
    <section className="py-20 bg-gray-900 text-center">
      <h3 className="text-4xl font-bold mb-10">Choose Your Plan</h3>
      <div className="grid md:grid-cols-4 gap-6 px-6 max-w-6xl mx-auto">
        {tiers.map((tier) => (
          <div
            key={tier.name}
            className="bg-gray-800 p-6 rounded-2xl shadow-lg border border-gray-700"
          >
            <h4 className="text-2xl font-semibold text-primary mb-2">{tier.name}</h4>
            <p className="text-3xl font-bold mb-4">{tier.price}</p>
            <ul className="text-gray-400 mb-6 space-y-2">
              {tier.features.map((f) => (
                <li key={f}>{f}</li>
              ))}
            </ul>
            <button
              onClick={() => handleClick(tier.stripeId)}
              className="btn w-full"
            >
              Select
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}
