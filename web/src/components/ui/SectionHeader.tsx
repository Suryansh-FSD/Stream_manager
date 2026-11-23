import React from "react";
import Link from "next/link";
import { ChevronRight } from "lucide-react";

interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  href?: string;
  actionText?: string;
}

export function SectionHeader({
  title,
  subtitle,
  href,
  actionText = "Show all",
}: SectionHeaderProps) {
  return (
    <div className="flex items-end justify-between mb-4">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white hover:underline cursor-pointer">
          {href ? <Link href={href}>{title}</Link> : title}
        </h2>
        {subtitle && <p className="text-xs text-muted mt-0.5">{subtitle}</p>}
      </div>

      {href && (
        <Link
          href={href}
          className="text-xs font-semibold text-muted hover:text-white flex items-center gap-1 transition-colors group"
        >
          <span>{actionText}</span>
          <ChevronRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
        </Link>
      )}
    </div>
  );
}
