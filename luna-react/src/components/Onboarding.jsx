import { useLuna } from "../hooks/useLuna.js";

export function Onboarding() {
  const { getOnboardingDone, setOnboardingDone } = useLuna();
  if (getOnboardingDone()) return null;

  return (
    <div className="onboarding-overlay">
      <p className="onboarding-brand">Luna</p>
      <p className="onboarding-tagline">
        Your space for wardrobe, daily rhythm, and gentle focus. Designed for the way you live.
      </p>
      <button type="button" className="btn btn-primary onboarding-cta" onClick={setOnboardingDone}>
        Get started
      </button>
      <p className="onboarding-footer">Designed by Lindsay</p>
    </div>
  );
}
