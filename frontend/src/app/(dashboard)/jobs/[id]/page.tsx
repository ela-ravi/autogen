import { redirect } from "next/navigation";

/** Always send job URLs to the Jobs list; it opens details in a modal via ?job= */
export default function JobDetailRedirectPage({
  params,
}: {
  params: { id: string };
}) {
  redirect(`/jobs?job=${encodeURIComponent(params.id)}`);
}
