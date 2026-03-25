interface UploadStatCardProps {
  title: string;
  imported: number;
  skipped: number;
}

export const UploadStatCard = ({ title, imported, skipped }: UploadStatCardProps) => {
  return (
    <div className="space-y-2">
      <p className="text-sm font-semibold text-gray-700 dark:text-gray-300">{title}</p>
      <div className="rounded p-3">
        <p className="text-2xl font-bold text-primary">{imported}</p>
        <p className="text-xs text-gray-600 dark:text-gray-400">imported</p>
      </div>
      <div className="rounded p-3">
        <p className="text-lg font-semibold text-amber-600 dark:text-amber-400">{skipped}</p>
        <p className="text-xs text-gray-600 dark:text-gray-400">skipped</p>
      </div>
    </div>
  );
};
