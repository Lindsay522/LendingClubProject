export const KEYS = {
  closet: "luna_closet_en",
  outfits: "luna_outfits_en",
  events: "luna_events_en",
  sleep: "luna_sleep_en",
  sport: "luna_sport_en",
  reflections: "luna_reflections_en",
  tomorrow: "luna_tomorrow_en",
  focus: "luna_focus_en",
  onboarding: "luna_onboarding_done_en",
};

export const MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export const ROOM_NAMES = {
  reset: "Soft reset",
  study: "Deep study",
  sleep: "Wind down",
  yoga: "Stretch break",
  morning: "Morning start",
  creative: "Creative focus",
};

export const ROOM_GUIDANCE = {
  reset: "Take a breath. Let today’s noise fade. You’re right here.",
  study: "One task at a time. Put your phone away and dive in.",
  sleep: "Dim the lights. This is your cue to slow down and rest.",
  yoga: "Stand or sit. Stretch gently. Breathe in, then out.",
  morning: "Start slow. Hydrate, move a little, then ease into your list.",
  creative: "No judgment. Let ideas flow. You can edit later.",
};

export const CATEGORY_ICONS = {
  Tops: "👕",
  Bottoms: "👖",
  Outerwear: "🧥",
  "Shoes & Bags": "👟",
  Accessories: "✨",
};

export const ROOM_FOCUS_SECONDS = {
  study: 25 * 60,
  creative: 25 * 60,
  morning: 10 * 60,
};

export const VALID_ROUTES = ["dashboard", "closet", "outfit", "planner", "rooms", "settings"];

export const OUTFIT_PROMPTS = {
  today: { name: "Today’s look", occasion: "Class" },
  onepiece: { name: "Built around one piece", occasion: "Other" },
  campus: { name: "Campus look", occasion: "Class" },
  interview: { name: "Interview ready", occasion: "Interview" },
  weekend: { name: "Weekend reset", occasion: "Other" },
};
