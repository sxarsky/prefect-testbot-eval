import { useSuspenseQuery } from "@tanstack/react-query";
import { CheckCircle, Clock } from "lucide-react";
import type { JSX } from "react";
import { buildGetFlowRunCheckpointsQuery } from "@/api/checkpoints";
import {
	Accordion,
	AccordionContent,
	AccordionItem,
	AccordionTrigger,
} from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type FlowRunCheckpointsProps = {
	flowRunId: string;
};

export function FlowRunCheckpoints({
	flowRunId,
}: FlowRunCheckpointsProps): JSX.Element {
	const { data: checkpointsData } = useSuspenseQuery(
		buildGetFlowRunCheckpointsQuery(flowRunId),
	);

	const getStateIcon = (state: string) => {
		if (state === "completed") {
			return <CheckCircle className="h-5 w-5 text-green-500" />;
		}
		return <Clock className="h-5 w-5 text-blue-500" />;
	};

	return (
		<Card>
			<CardHeader>
				<CardTitle>
					Checkpoints ({checkpointsData.total_checkpoints})
				</CardTitle>
			</CardHeader>
			<CardContent>
				<div className="relative">
					{/* Timeline line */}
					<div className="absolute left-[11px] top-0 h-full w-0.5 bg-border" />

					{/* Checkpoints */}
					<Accordion type="single" collapsible className="w-full">
						{checkpointsData.checkpoints.map((checkpoint, index) => (
							<AccordionItem key={checkpoint.id} value={checkpoint.id}>
								<AccordionTrigger className="hover:no-underline">
									<div className="flex items-start gap-3">
										<div className="relative z-10 mt-1">
											{getStateIcon(checkpoint.state)}
										</div>
										<div className="flex-1 text-left">
											<div className="flex items-center gap-2">
												<span className="font-medium">{checkpoint.name}</span>
												<Badge variant="outline" className="text-xs">
													{checkpoint.state}
												</Badge>
											</div>
											<p className="text-sm text-muted-foreground">
												{new Date(checkpoint.created_at).toLocaleString()}
											</p>
										</div>
									</div>
								</AccordionTrigger>
								<AccordionContent>
									<div className="ml-11 space-y-2 text-sm">
										<div className="rounded-md bg-muted p-3">
											<p className="mb-2 font-medium">Metadata:</p>
											<pre className="text-xs">
												{JSON.stringify(checkpoint.metadata, null, 2)}
											</pre>
										</div>
									</div>
								</AccordionContent>
							</AccordionItem>
						))}
					</Accordion>
				</div>
			</CardContent>
		</Card>
	);
}
