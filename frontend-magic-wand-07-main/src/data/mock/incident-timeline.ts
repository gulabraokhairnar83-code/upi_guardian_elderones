import type { LucideIcon } from "lucide-react";
import {
  IndianRupee,
  MessageSquare,
  Phone,
  ShieldAlert,
  Users,
} from "lucide-react";

export interface TimelineEvent {
  time: string;
  text: string;
  icon: LucideIcon;
}

export const incidentTimeline: TimelineEvent[] = [
  { time: "11:15 PM", text: "Suspicious SMS received", icon: MessageSquare },
  { time: "11:29 PM", text: "Scam-like call detected", icon: Phone },
  {
    time: "11:42 PM",
    text: "₹35,000 UPI transaction initiated",
    icon: IndianRupee,
  },
  {
    time: "11:43 PM",
    text: "High-risk transaction detected",
    icon: ShieldAlert,
  },
  { time: "11:44 PM", text: "Family alert generated", icon: Users },
];
