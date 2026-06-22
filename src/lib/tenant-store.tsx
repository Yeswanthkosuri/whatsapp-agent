import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { tenants as mockTenants } from "@/lib/mock-data";
import type { Tenant } from "@/types";
import { tenantService } from "@/services/tenantService";
import { isApiConfigured } from "@/services/api";

type TenantContextValue = {
  current: Tenant;
  setCurrent: (t: Tenant) => void;
  all: Tenant[];
  isLoading: boolean;
};

const TenantContext = createContext<TenantContextValue | null>(null);

export function TenantProvider({ children }: { children: ReactNode }) {
  const [all, setAll] = useState<Tenant[]>(mockTenants);
  const [current, setCurrent] = useState<Tenant>(mockTenants[0]);
  const [isLoading, setIsLoading] = useState(isApiConfigured());

  useEffect(() => {
    if (!isApiConfigured()) return;
    setIsLoading(true);
    tenantService
      .list()
      .then((data) => {
        if (data.length > 0) {
          setAll(data);
          setCurrent(data[0]);
        }
      })
      .catch(() => {
        setAll(mockTenants);
        setCurrent(mockTenants[0]);
      })
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <TenantContext.Provider value={{ current, setCurrent, all, isLoading }}>
      {children}
    </TenantContext.Provider>
  );
}

export function useTenant() {
  const ctx = useContext(TenantContext);
  if (!ctx) throw new Error("useTenant must be used inside TenantProvider");
  return ctx;
}
