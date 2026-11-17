import type { ReactNode } from "react";

/** A section's head, on the page grid: label and title in the main columns, the paragraph in the side columns.
    Every section body uses the same two column groups, so heads, trays and text all start on the same lines. */
export function Head({
  label,
  title,
  text,
  id,
  children,
}: {
  label: string;
  title: ReactNode;
  text?: ReactNode;
  id?: string;
  children?: ReactNode;
}) {
  return (
    <div className="wrap grid head">
      <div className="span-main">
        <p className="label">{label}</p>
        <h2 id={id} className="h2">
          {title}
        </h2>
      </div>
      {(text || children) && (
        <div className="span-side head__text">
          {text && <p>{text}</p>}
          {children}
        </div>
      )}
    </div>
  );
}
