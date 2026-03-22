import { useSuspenseQuery } from "@tanstack/react-query";
import type { JSX } from "react";
import {
	buildGetCostHistoryQuery,
	buildGetFlowCostProfileQuery,
} from "@/api/flow-costs";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
	Area,
	AreaChart,
	CartesianGrid,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts";

type FlowCostsTabProps = {
	flowId: string;
};

export function FlowCostsTab({ flowId }: FlowCostsTabProps): JSX.Element {
	const { data: costData } = useSuspenseQuery(
		buildGetFlowCostProfileQuery(flowId),
	);
	const { data: historyData } = useSuspenseQuery(
		buildGetCostHistoryQuery(flowId, 30),
	);

	const { cost_profile, current_spending } = costData;

	return (
		<div className="flex flex-col gap-4">
			<Card>
				<CardHeader>
					<CardTitle>Cost Profile</CardTitle>
				</CardHeader>
				<CardContent>
					<div className="grid grid-cols-2 gap-4 md:grid-cols-4">
						<div>
							<p className="text-sm text-muted-foreground">Currency</p>
							<p className="text-lg font-semibold">{cost_profile.currency}</p>
						</div>
						<div>
							<p className="text-sm text-muted-foreground">Cost Per Second</p>
							<p className="text-lg font-semibold">
								{cost_profile.cost_per_second.toFixed(4)}
							</p>
						</div>
						<div>
							<p className="text-sm text-muted-foreground">Cost Per Task</p>
							<p className="text-lg font-semibold">
								{cost_profile.cost_per_task.toFixed(2)}
							</p>
						</div>
						<div>
							<p className="text-sm text-muted-foreground">Fixed Cost/Run</p>
							<p className="text-lg font-semibold">
								{cost_profile.fixed_cost_per_run.toFixed(2)}
							</p>
						</div>
					</div>
				</CardContent>
			</Card>

			<Card>
				<CardHeader>
					<CardTitle>Current Spending</CardTitle>
				</CardHeader>
				<CardContent>
					<div className="grid grid-cols-2 gap-4 md:grid-cols-5">
						<div>
							<p className="text-sm text-muted-foreground">Total Cost</p>
							<p className="text-2xl font-bold text-blue-500">
								${current_spending.total_cost.toFixed(2)}
							</p>
						</div>
						<div>
							<p className="text-sm text-muted-foreground">Total Runs</p>
							<p className="text-2xl font-bold">{current_spending.total_runs}</p>
						</div>
						<div>
							<p className="text-sm text-muted-foreground">Total Tasks</p>
							<p className="text-2xl font-bold">
								{current_spending.total_tasks}
							</p>
						</div>
						<div>
							<p className="text-sm text-muted-foreground">Duration</p>
							<p className="text-2xl font-bold">
								{Math.floor(current_spending.total_duration_seconds / 60)}m
							</p>
						</div>
						<div>
							<p className="text-sm text-muted-foreground">Avg Cost/Run</p>
							<p className="text-2xl font-bold text-green-500">
								${current_spending.average_cost_per_run.toFixed(3)}
							</p>
						</div>
					</div>
				</CardContent>
			</Card>

			<Card>
				<CardHeader>
					<CardTitle>Cost History (30 Days)</CardTitle>
				</CardHeader>
				<CardContent>
					<ResponsiveContainer width="100%" height={300}>
						<AreaChart data={historyData.history}>
							<defs>
								<linearGradient id="costGradient" x1="0" y1="0" x2="0" y2="1">
									<stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
									<stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
								</linearGradient>
							</defs>
							<CartesianGrid strokeDasharray="3 3" />
							<XAxis
								dataKey="date"
								tickFormatter={(value) => {
									const date = new Date(value);
									return `${date.getMonth() + 1}/${date.getDate()}`;
								}}
							/>
							<YAxis tickFormatter={(value) => `$${value.toFixed(2)}`} />
							<Tooltip />
							<Area
								type="monotone"
								dataKey="total_cost"
								stroke="#3b82f6"
								strokeWidth={2}
								fill="url(#costGradient)"
							/>
						</AreaChart>
					</ResponsiveContainer>
				</CardContent>
			</Card>
		</div>
	);
}
