"use client";

import { createContext, useContext } from "react";

export type AppMetaValue = {
  google_client_id: string | null;
};

const defaultMeta: AppMetaValue = { google_client_id: null };

export const AppMetaContext = createContext<AppMetaValue>(defaultMeta);

export function useAppMeta() {
  return useContext(AppMetaContext);
}
