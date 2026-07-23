import { LeaderboardHubStoryboard, type LeaderboardScope } from "@vibemaxxing/ui/competition-suite";

const routeScopes: Record<string, LeaderboardScope> = {
  global: "Global",
  friends: "Friends",
  boards: "Boards",
  organizations: "Organizations",
};

export function generateStaticParams() {
  return Object.keys(routeScopes).map((scope) => ({ scope }));
}

export default async function LeaderboardScopePage({ params }: { params: Promise<{ scope: string }> }) {
  const { scope } = await params;
  return <LeaderboardHubStoryboard initialScope={routeScopes[scope] ?? "Global"} />;
}
