import { queryOptions, useMutation, useQueryClient } from "@tanstack/react-query";
import { getQueryService } from "@/api/service";

export type CostProfile = {
	id: string;
	flow_id: string;
	currency: string;
	cost_per_second: number;
	cost_per_task: number;
	cost_per_gb_memory: number;
	fixed_cost_per_run: number;
	created_at: string;
	updated_at: string;
};

export type CurrentSpending = {
	total_cost: number;
	total_runs: number;
	total_tasks: number;
	total_duration_seconds: number;
	average_cost_per_run: number;
};

export type FlowCostProfileResponse = {
	flow_id: string;
	cost_profile: CostProfile;
	current_spending: CurrentSpending;
};

export type CostHistoryEntry = {
	date: string;
	total_cost: number;
	run_count: number;
	average_cost_per_run: number;
	total_duration_seconds: number;
};

export type CostHistoryResponse = {
	flow_id: string;
	period_days: number;
	total_cost: number;
	total_runs: number;
	history: CostHistoryEntry[];
};

export const queryKeyFactory = {
	all: () => ["flow-costs"] as const,
	costProfile: (flowId: string) =>
		[...queryKeyFactory.all(), "profile", flowId] as const,
	costHistory: (flowId: string, days: number) =>
		[...queryKeyFactory.all(), "history", flowId, days] as const,
};

export const buildGetFlowCostProfileQuery = (flowId: string) =>
	queryOptions({
		queryKey: queryKeyFactory.costProfile(flowId),
		queryFn: async (): Promise<FlowCostProfileResponse> => {
			const res = await (
				await getQueryService()
			).GET("/flow-costs-v2/flows/{flow_id}/cost-profile/", {
				params: { path: { flow_id: flowId } },
			});
			if (!res.data) {
				throw new Error("'data' expected");
			}
			return res.data as FlowCostProfileResponse;
		},
		staleTime: 30000,
	});

export const buildGetCostHistoryQuery = (flowId: string, days: number = 30) =>
	queryOptions({
		queryKey: queryKeyFactory.costHistory(flowId, days),
		queryFn: async (): Promise<CostHistoryResponse> => {
			const res = await (
				await getQueryService()
			).GET("/flow-costs-v2/flows/{flow_id}/cost-history/", {
				params: {
					path: { flow_id: flowId },
					query: { days },
				},
			});
			if (!res.data) {
				throw new Error("'data' expected");
			}
			return res.data as CostHistoryResponse;
		},
		staleTime: 60000,
	});

export const useCreateCostProfile = () => {
	const queryClient = useQueryClient();

	const { mutate: createCostProfile, ...rest } = useMutation({
		mutationFn: async ({
			flowId,
			data,
		}: {
			flowId: string;
			data: {
				currency: string;
				cost_per_second: number;
				cost_per_task: number;
				cost_per_gb_memory: number;
				fixed_cost_per_run: number;
			};
		}) => {
			const res = await (
				await getQueryService()
			).POST("/flow-costs-v2/flows/{flow_id}/cost-profile/", {
				params: { path: { flow_id: flowId } },
				body: data as never,
			});
			if (!res.data) {
				throw new Error("'data' expected");
			}
			return res.data as CostProfile;
		},
		onSuccess: (_, variables) => {
			void queryClient.invalidateQueries({
				queryKey: queryKeyFactory.costProfile(variables.flowId),
			});
		},
	});

	return { createCostProfile, ...rest };
};
