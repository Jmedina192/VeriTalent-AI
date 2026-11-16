import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "VeriTalent-AI | Recruiter Dashboard", description: "Human-reviewed technical résumé comparisons" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
