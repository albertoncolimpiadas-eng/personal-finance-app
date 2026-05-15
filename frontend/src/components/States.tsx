export function LoadingState({ label = "Loading" }: { label?: string }) {
  return <div className="state">{label}...</div>;
}

export function ErrorState({ message }: { message: string }) {
  return <div className="state error-state">{message}</div>;
}

export function EmptyState({ message }: { message: string }) {
  return <div className="state">{message}</div>;
}
