import type { ReactNode } from "react";

/** A section's head: label and title on the left, the paragraph on the right, on its own row of the sheet. */
export function Head({
  label,
  title,
  text,
  id,
  center = false,
  children,
}: {
  label: string;
  title: ReactNode;
  text?: ReactNode;
  id?: string;
  center?: boolean;
  children?: ReactNode;
}) {
  return (
    <div className={center ? "wrap head head--center" : "wrap head"}>
      <div>
        <p className="label">{label}</p>
        <h2 id={id} className="h2">
          {title}
        </h2>
      </div>
      {(text || children) && (
        <div className="head__text">
          {text && <p>{text}</p>}
          {children}
        </div>
      )}
    </div>
  );
}
