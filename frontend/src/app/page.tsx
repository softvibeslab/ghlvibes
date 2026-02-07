import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-140px)]">
      <div className="text-center space-y-6">
        <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
          GoHighLevel Clone
        </h1>
        <p className="text-lg text-muted-foreground max-w-[600px] mx-auto">
          Automate your business with powerful workflow automation. Create,
          manage, and optimize your workflows with our intuitive visual builder.
        </p>
        <div className="flex gap-4 justify-center">
          <Button asChild size="lg">
            <Link href="/workflows">View Workflows</Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link href="/workflows/create">Create Workflow</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
