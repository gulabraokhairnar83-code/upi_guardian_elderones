export type ElderProfile = {
  id: string;
  name: string;
  age: number;
  location: string;
  accountSafetyStatus: "Protected" | "At Risk" | "Review Required";
  phone: string;
  email: string;
  twoFactorEnabled: boolean;
  loginAlertsEnabled: boolean;
  metrics: {
    currentRiskScore: number;
    todayTransactionsCount: number;
    activeAlertsCount: number;
    scamCommunicationsCount: number;
  };
};

export const elderProfile: ElderProfile = {
  id: "elder-sunita-01",
  name: "Sunita Devi",
  age: 68,
  location: "Pune",
  accountSafetyStatus: "Protected",
  phone: "+91 ••••• ••410",
  email: "sunita.demo@example.com",
  twoFactorEnabled: true,
  loginAlertsEnabled: true,
  metrics: {
    currentRiskScore: 27,
    todayTransactionsCount: 8,
    activeAlertsCount: 2,
    scamCommunicationsCount: 3,
  },
};
