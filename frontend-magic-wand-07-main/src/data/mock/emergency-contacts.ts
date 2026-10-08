export type EmergencyContact = {
  id: string;
  name: string;
  relation: string;
  phone: string;
  isTrusted: boolean;
};

export const emergencyContacts: EmergencyContact[] = [
  {
    id: "ec-1",
    name: "Rajesh Devi",
    relation: "Son",
    phone: "+91 98201 12345",
    isTrusted: true,
  },
  {
    id: "ec-2",
    name: "Kavita Rao",
    relation: "Daughter",
    phone: "+91 98202 23456",
    isTrusted: true,
  },
  {
    id: "ec-3",
    name: "Dr. Mehta",
    relation: "Trusted Contact",
    phone: "+91 98203 34567",
    isTrusted: true,
  },
];
