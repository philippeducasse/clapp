"use client";

import { useState } from "react";
import Link from "next/link";
import { Check, ChevronDown, ExternalLink, Pencil, Undo2, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  AcceptOverrides,
  DISMISS_REASON_LABELS,
  DiscoveryCandidate,
  DiscoveryCandidateState,
  DiscoveryOrgType,
  DismissReason,
} from "@/interfaces/entities/Discovery";
import {
  candidateApplicationDates,
  candidateDates,
  candidateLocation,
  hopLabel,
  ORG_TYPE_LABELS,
  seedUrl,
} from "../helpers/discoveryLabels";

interface DiscoveryCandidateItemProps {
  candidate: DiscoveryCandidate;
  onAccept: (candidate: DiscoveryCandidate, overrides: AcceptOverrides) => Promise<void>;
  onDismiss: (candidate: DiscoveryCandidate, reason: DismissReason) => Promise<void>;
  onRestore: (candidate: DiscoveryCandidate) => Promise<void>;
}

const DiscoveryCandidateItem = ({
  candidate,
  onAccept,
  onDismiss,
  onRestore,
}: DiscoveryCandidateItemProps) => {
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(candidate.name);
  const [orgType, setOrgType] = useState<DiscoveryOrgType>(candidate.orgType);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const reviewable =
    candidate.state === DiscoveryCandidateState.PENDING ||
    candidate.state === DiscoveryCandidateState.UNRESOLVED;
  const dates = candidateDates(candidate);
  const applicationDates = candidateApplicationDates(candidate);
  const location = candidateLocation(candidate);
  const acceptedUrl = seedUrl(candidate);

  const run = async (action: () => Promise<void>) => {
    setIsSubmitting(true);
    try {
      await action();
    } catch (error) {
      console.error("Discovery action failed:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const overrides = (): AcceptOverrides => {
    const changes: AcceptOverrides = {};
    if (name.trim() && name.trim() !== candidate.name) changes.name = name.trim();
    if (orgType !== candidate.orgType) changes.orgType = orgType;
    return changes;
  };

  return (
    <div className="p-3 rounded-lg border space-y-2">
      <div className="flex justify-between items-start gap-2">
        <div className="min-w-0 space-y-1">
          {isEditing ? (
            <div className="flex flex-wrap gap-2">
              <Input
                value={name}
                onChange={(event) => setName(event.target.value)}
                className="w-72"
                aria-label="Name"
              />
              <Select value={orgType} onValueChange={(value) => setOrgType(value as DiscoveryOrgType)}>
                <SelectTrigger className="w-40" aria-label="Type">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Object.values(DiscoveryOrgType).map((type) => (
                    <SelectItem key={type} value={type}>
                      {ORG_TYPE_LABELS[type]}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          ) : (
            <p className="font-medium text-lg break-words">
              {candidate.name}{" "}
              <span className="text-muted-foreground text-sm">
                {ORG_TYPE_LABELS[candidate.orgType]}
                {location && ` · ${location}`}
              </span>
            </p>
          )}
          {candidate.websiteUrl && (
            <a
              href={candidate.websiteUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline text-sm inline-flex items-center gap-1 break-all"
            >
              {candidate.websiteUrl} <ExternalLink className="h-3 w-3" />
            </a>
          )}
        </div>
        <div className="flex flex-wrap gap-1 shrink-0 justify-end">
          {candidate.subtype && <Badge variant="outline">{candidate.subtype.toLowerCase()}</Badge>}
          {candidate.applicationType && (
            <Badge variant="outline">apply: {candidate.applicationType.toLowerCase()}</Badge>
          )}
          {candidate.run && <Badge variant="outline">run #{candidate.run}</Badge>}
        </div>
      </div>

      {candidate.description && <p>{candidate.description}</p>}

      <div className="text-sm space-y-0.5">
        {dates && <p>Dates: {dates}</p>}
        {applicationDates && <p>Applications: {applicationDates}</p>}
        {candidate.applicationUrl && (
          <p>
            Apply at:{" "}
            <a
              href={candidate.applicationUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline break-all"
            >
              {candidate.applicationUrl}
            </a>
          </p>
        )}
        {candidate.contacts.length > 0 && (
          <p>
            Contacts:{" "}
            {candidate.contacts
              .map((c) => [c.name, c.email, c.role && `(${c.role})`].filter(Boolean).join(" "))
              .join("; ")}
          </p>
        )}
      </div>

      {candidate.relevanceReason && <p className="italic">{candidate.relevanceReason}</p>}

      {candidate.foundVia.length > 0 && (
        <p className="text-sm text-muted-foreground flex flex-wrap items-center gap-1">
          Found via:
          {candidate.foundVia.map((hop, index) => (
            <span key={`${hop.url}-${index}`} className="inline-flex items-center gap-1">
              {index > 0 && <span>→</span>}
              <a
                href={hop.url}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:underline text-primary"
                title={[hop.title, hop.snippet].filter(Boolean).join(" — ") || hop.url}
              >
                {hopLabel(hop.kind)}
              </a>
            </span>
          ))}
        </p>
      )}

      {candidate.sources.length > 0 && (
        <details>
          <summary className="cursor-pointer text-sm text-muted-foreground">
            Sources ({candidate.sources.length})
          </summary>
          <ul className="mt-2 space-y-2 text-sm">
            {candidate.sources.map((source) => (
              <li key={source.url}>
                <a
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline break-all"
                >
                  {source.title || source.url}
                </a>
                {source.snippet && <p className="text-muted-foreground">{source.snippet}</p>}
              </li>
            ))}
          </ul>
        </details>
      )}

      <div className="flex flex-wrap items-center gap-2">
        {reviewable && (
          <>
            <Button
              size="sm"
              disabled={isSubmitting || (isEditing && !name.trim())}
              onClick={() => run(() => onAccept(candidate, overrides()))}
            >
              <Check /> Accept
            </Button>
            {!isEditing && (
              <Button
                size="sm"
                variant="outline"
                disabled={isSubmitting}
                onClick={() => setIsEditing(true)}
              >
                <Pencil /> Edit name and type
              </Button>
            )}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button size="sm" variant="outline" disabled={isSubmitting}>
                  <X /> Dismiss <ChevronDown />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                {Object.values(DismissReason).map((reason) => (
                  <DropdownMenuItem
                    key={reason}
                    onSelect={() => run(() => onDismiss(candidate, reason))}
                  >
                    {DISMISS_REASON_LABELS[reason]}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
            <span className="text-sm text-muted-foreground">
              Accepting adds it for all users.
            </span>
          </>
        )}
        {candidate.state === DiscoveryCandidateState.ACCEPTED && (
          <>
            <Badge variant="outline" className="bg-green-100 text-green-700 border-green-200">
              Added for all users
            </Badge>
            {acceptedUrl && (
              <Link href={acceptedUrl} className="text-primary hover:underline text-sm">
                Open
              </Link>
            )}
          </>
        )}
        {candidate.state === DiscoveryCandidateState.DISMISSED && (
          <>
            <Badge variant="outline">
              Dismissed
              {candidate.dismissReason && `: ${DISMISS_REASON_LABELS[candidate.dismissReason]}`}
            </Badge>
            <Button
              size="sm"
              variant="outline"
              disabled={isSubmitting}
              onClick={() => run(() => onRestore(candidate))}
            >
              <Undo2 /> Move back to review
            </Button>
          </>
        )}
      </div>
    </div>
  );
};

export default DiscoveryCandidateItem;
