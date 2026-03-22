import { queryOptions, useMutation, useQueryClient } from "@tanstack/react-query";
import { getQueryService } from "@/api/service";

export type Checkpoint = {
	id: string;
	name: string;
	state: string;
	created_at: string;
	metadata: Record<string, unknown>;
};

export type FlowRunCheckpointsResponse = {
	flow_run_id: string;
	checkpoints: Checkpoint[];
	total_checkpoints: number;
	latest_checkpoint_id: string;
};

export const queryKeyFactory = {
	all: () => ["checkpoints"] as const,
	flowRunCheckpoints: (flowRunId: string) =>
		[...queryKeyFactory.all(), "flow-run", flowRunId] as const,
	checkpointDetails: (checkpointId: string) =>
		[...queryKeyFactory.all(), "details", checkpointId] as const,
};

export const buildGetFlowRunCheckpointsQuery = (flowRunId: string) =>
	queryOptions({
		queryKey: queryKeyFactory.flowRunCheckpoints(flowRunId),
		queryFn: async (): Promise<FlowRunCheckpointsResponse> => {
			const res = await (
				await getQueryService()
			).GET("/checkpoints-v2/flow-runs/{flow_run_id}/checkpoints/", {
				params: { path: { flow_run_id: flowRunId } },
			});
			if (!res.data) {
				throw new Error("'data' expected");
			}
			return res.data as FlowRunCheckpointsResponse;
		},
		staleTime: 30000,
	});

export const useCreateCheckpoint = () => {
	const queryClient = useQueryClient();

	const { mutate: createCheckpoint, ...rest } = useMutation({
		mutationFn: async ({
			flowRunId,
			data,
		}: {
			flowRunId: string;
			data: { name: string; metadata?: Record<string, unknown> };
		}) => {
			const res = await (
				await getQueryService()
			).POST("/checkpoints-v2/flow-runs/{flow_run_id}/checkpoints/", {
				params: { path: { flow_run_id: flowRunId } },
				body: data as never,
			});
			if (!res.data) {
				throw new Error("'data' expected");
			}
			return res.data as Checkpoint;
		},
		onSuccess: (_, variables) => {
			void queryClient.invalidateQueries({
				queryKey: queryKeyFactory.flowRunCheckpoints(variables.flowRunId),
			});
		},
	});

	return { createCheckpoint, ...rest };
};
