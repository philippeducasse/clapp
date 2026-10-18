"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useSelector } from "react-redux";
import { Compass } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { discoveryApiService } from "@/api/discoveryApiService";
import {
  AcceptOverrides,
  DiscoveryCandidate,
  DiscoveryCandidateState,
  DiscoveryRun,
  DismissReason,
} from "@/interfaces/entities/Discovery";
import { selectProfile } from "@/redux/slices/authSlice";
import { useAppDispatch } from "@/redux/hook";
import StartingPointBar from "@/components/page-components/discover/components/StartingPointBar";
import DiscoveryRunPanel from "@/components/page-components/discover/components/DiscoveryRunPanel";
import DiscoveryCandidateItem from "@/components/page-components/discover/components/DiscoveryCandidateItem";
import { refreshAcceptedSeed } from "@/components/page-components/discover/helpers/refreshAcceptedSeed";

const POLL_INTERVAL_MS = 3000;

const TABS: { state: DiscoveryCandidateState; label: string; emptyText: string }[] = [
  { state: DiscoveryCandidateState.PENDING, label: "To review", emptyText: "Nothing to review" },
  {
    state: DiscoveryCandidateState.UNRESOLVED,
    label: "Unresolved",
    emptyText: "No unresolved candidates",
  },
  { state: DiscoveryCandidateState.ACCEPTED, label: "Accepted", emptyText: "Nothing accepted yet" },
  {
    state: DiscoveryCandidateState.DISMISSED,
    label: "Dismissed",
    emptyText: "No dismissed candidates",
  },
];

const fetchAllCandidates = () =>
  Promise.all(TABS.map((tab) => discoveryApiService.getCandidates({ state: tab.state })));

const DiscoverPage = () => {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const profile = useSelector(selectProfile);
  const isSuperuser = profile?.isSuperuser === true;

  const [runs, setRuns] = useState<DiscoveryRun[]>([]);
  const [run, setRun] = useState<DiscoveryRun | null>(null);
  const [candidates, setCandidates] = useState<DiscoveryCandidate[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (profile && !isSuperuser) router.replace("/dashboard");
  }, [profile, isSuperuser, router]);

  const loadCandidates = useCallback(async () => {
    const responses = await fetchAllCandidates();
    setCandidates(responses.flatMap((data) => data.results));
  }, []);

  const loadRuns = useCallback(async () => {
    const data = await discoveryApiService.getRuns();
    setRuns(data.results);
  }, []);

  useEffect(() => {
    if (!isSuperuser) return;
    Promise.all([discoveryApiService.getRuns(), fetchAllCandidates()])
      .then(([recent, candidateLists]) => {
        setRuns(recent.results);
        setRun((current) => current ?? recent.results[0] ?? null);
        setCandidates(candidateLists.flatMap((data) => data.results));
      })
      .catch((error) => console.error("Failed to load discovery:", error))
      .finally(() => setIsLoading(false));
  }, [isSuperuser]);

  // Poll the shown run while it's active; reload the lists once it finishes.
  const runId = run?.id;
  const runIsActive = run?.isActive ?? false;
  useEffect(() => {
    if (!runId || !runIsActive) return;
    const timer = setInterval(async () => {
      try {
        const updated = await discoveryApiService.getRun(runId);
        setRun((current) => (current?.id === updated.id ? updated : current));
        setRuns((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
        if (!updated.isActive) {
          await loadCandidates();
        }
      } catch (error) {
        console.error("Failed to poll the discovery run:", error);
      }
    }, POLL_INTERVAL_MS);
    return () => clearInterval(timer);
  }, [runId, runIsActive, loadCandidates]);

  const hasActiveRun = runs.some((item) => item.isActive) || runIsActive;

  const handleStart = async (startingPoint: string): Promise<boolean> => {
    try {
      const created = await discoveryApiService.startRun(startingPoint);
      setRun(created);
      setRuns((prev) => [created, ...prev.filter((item) => item.id !== created.id)]);
      return true;
    } catch (error) {
      console.error("Failed to start discovery:", error);
      // Most likely another run is active (409): show it.
      loadRuns().catch(() => undefined);
      return false;
    }
  };

  const handleSelectRun = async (id: number) => {
    const selected = runs.find((item) => item.id === id) ?? null;
    setRun(selected);
    try {
      setRun(await discoveryApiService.getRun(id));
    } catch (error) {
      console.error("Failed to load the discovery run:", error);
    }
  };

  const handleCancel = async (target: DiscoveryRun) => {
    try {
      setRun(await discoveryApiService.cancelRun(target.id));
    } catch (error) {
      console.error("Failed to cancel the discovery run:", error);
    }
  };

  const replaceCandidate = (updated: DiscoveryCandidate) =>
    setCandidates((prev) => prev.map((c) => (c.id === updated.id ? updated : c)));

  const handleAccept = async (candidate: DiscoveryCandidate, overrides: AcceptOverrides) => {
    const accepted = await discoveryApiService.accept(candidate.id, overrides);
    replaceCandidate(accepted);
    await refreshAcceptedSeed(accepted, dispatch);
  };

  const handleDismiss = async (candidate: DiscoveryCandidate, reason: DismissReason) =>
    replaceCandidate(await discoveryApiService.dismiss(candidate.id, reason));

  const handleRestore = async (candidate: DiscoveryCandidate) =>
    replaceCandidate(await discoveryApiService.restore(candidate.id));

  if (!isSuperuser) {
    return (
      <div className="container mx-auto p-6">
        <Skeleton className="h-10 w-full" />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-3xl text-primary flex items-center gap-2">
            <Compass /> Discover
          </CardTitle>
          <CardDescription className="text-xl">
            Find festivals, residencies and venues clapp doesn&apos;t have yet. Start from an
            artist&apos;s website, a request in plain words, or both. Nothing is added until you
            accept it.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <StartingPointBar disabled={hasActiveRun} onStart={handleStart} />
          {isLoading ? (
            <Skeleton className="h-24 w-full" />
          ) : (
            <DiscoveryRunPanel
              run={run}
              runs={runs}
              onSelectRun={handleSelectRun}
              onCancel={handleCancel}
            />
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-2xl text-primary">Candidates</CardTitle>
          <CardDescription>
            Accepted candidates are added for all users. Every candidate shows how it was found
            and which pages its facts came from.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue={DiscoveryCandidateState.PENDING}>
            <TabsList>
              {TABS.map((tab) => (
                <TabsTrigger key={tab.state} value={tab.state}>
                  {tab.label} ({candidates.filter((c) => c.state === tab.state).length})
                </TabsTrigger>
              ))}
            </TabsList>
            {TABS.map((tab) => {
              const list = candidates.filter((c) => c.state === tab.state);
              return (
                <TabsContent key={tab.state} value={tab.state} className="mt-3">
                  {isLoading ? (
                    <Skeleton className="h-6 w-full" />
                  ) : list.length === 0 ? (
                    <p className="text-muted-foreground text-sm">{tab.emptyText}</p>
                  ) : (
                    <div className="space-y-3">
                      {list.map((candidate) => (
                        <DiscoveryCandidateItem
                          key={`${candidate.id}-${candidate.state}`}
                          candidate={candidate}
                          onAccept={handleAccept}
                          onDismiss={handleDismiss}
                          onRestore={handleRestore}
                        />
                      ))}
                    </div>
                  )}
                </TabsContent>
              );
            })}
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default DiscoverPage;
