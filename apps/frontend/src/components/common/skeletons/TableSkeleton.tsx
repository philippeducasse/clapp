import { Skeleton } from "@/components/ui/skeleton"

export default function TableSkeleton() {
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-10 w-32" />
      </div>
      
      <div className="border rounded-lg">
        <div className="grid grid-cols-4 gap-4 p-4 border-b bg-muted/50">
          <Skeleton className="h-4" />
          <Skeleton className="h-4" />
          <Skeleton className="h-4" />
          <Skeleton className="h-4" />
        </div>
        
        {[...Array(8)].map((_, i) => (
          <div key={i} className="grid grid-cols-4 gap-4 p-4 border-b last:border-0">
            <Skeleton className="h-4" />
            <Skeleton className="h-4" />
            <Skeleton className="h-4" />
            <Skeleton className="h-4" />
          </div>
        ))}
      </div>
    </div>
  )
}