<template>
	<div class="py-4 relative min-h-[75vh] flex flex-col">
		<div class="flex gap-2 px-2">
			<Button
				:variant="listKind === 'procedures' ? 'solid' : 'subtle'"
				label="Procedures"
				@click="listKind = 'procedures'"
			/>
			<Button
				:variant="listKind === 'labs' ? 'solid' : 'subtle'"
				label="Lab Tests"
				@click="listKind = 'labs'"
			/>
		</div>

		<div v-if="!listLoaded" class="flex-1"></div>
		<div v-else-if="paginatedItems.length" class="flex-1 overflow-y-auto p-2">
			<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
				<Card
					v-for="(item, index) in paginatedItems"
					:key="`${item.encounter}-${itemTitle(item)}-${index}`"
					class="cursor-pointer rounded-xl border border-gray-200 transition-transform
						hover:scale-105 duration-200 hover:drop-shadow-md p-2 bg-surface-white
						min-h-[170px] min-w-[240px] !shadow-none drop-shadow-xl"
					@click="openItem(item)"
				>
					<div class="flex items-center justify-between gap-2">
						<h3 class="text-md font-semibold text-gray-800 truncate">{{ itemTitle(item) }}</h3>
						<Badge v-if="listKind === 'labs' && item.priority" variant="outline" theme="orange">
							{{ item.priority }}
						</Badge>
					</div>
					<p v-if="listKind === 'procedures'" class="mt-2 text-xs text-gray-600">
						<span v-if="item.date">{{ formatDate(item.date) }}</span>
						<span v-if="item.no_of_sessions"> · {{ item.no_of_sessions }} sessions</span>
					</p>
					<p v-if="itemComment(item)" class="mt-2 text-xs text-gray-600 line-clamp-2">
						{{ itemComment(item) }}
					</p>
					<p class="mt-2 text-xs text-gray-500">
						<FeatherIcon name="calendar" class="inline w-3 h-3 mr-1 text-gray-500" />
						{{ formatDate(item.encounter_date) }}
					</p>
					<p class="mt-1 text-xs text-gray-500 truncate">{{ item.practitioner_name }}</p>
				</Card>
			</div>
		</div>

		<div v-else class="flex flex-col items-center justify-center flex-grow text-center p-6">
			<FeatherIcon name="file-text" class="w-12 h-12 text-gray-400 mb-3" />
			<h2 class="text-lg font-semibold text-gray-700">No Records Found</h2>
			<p class="text-sm text-gray-500">{{ emptyMessage }}</p>
		</div>

		<div v-if="paginatedItems.length" class="flex justify-center items-center space-x-2 mt-auto pt-2">
			<Button variant="subtle" :disabled="currentPage === 1" @click="currentPage--">Prev</Button>
			<span class="text-sm text-gray-600">Page {{ currentPage }} of {{ totalPages }}</span>
			<Button variant="subtle" :disabled="currentPage === totalPages" @click="currentPage++">Next</Button>
		</div>
	</div>

	<Dialog v-model="procedure_open" :options="{ size: '3xl' }">
		<template #body-title>
			<h2 class="text-xl font-semibold text-gray-900">Procedure</h2>
			<p class="py-2 text-sm text-gray-500"># {{ selectedProcedure.encounter }}</p>
		</template>
		<template #body-content>
			<div class="space-y-3 text-sm text-gray-700">
				<p><span class="font-medium text-gray-900">Name:</span> {{ selectedProcedure.procedure_name || "—" }}</p>
				<p><span class="font-medium text-gray-900">Date:</span> {{ formatDate(selectedProcedure.date) }}</p>
				<p><span class="font-medium text-gray-900">Sessions:</span> {{ selectedProcedure.no_of_sessions || "—" }}</p>
				<p><span class="font-medium text-gray-900">Practitioner:</span> {{ selectedProcedure.practitioner_name || "—" }}</p>
				<p><span class="font-medium text-gray-900">Department:</span> {{ selectedProcedure.medical_department || "—" }}</p>
				<p class="whitespace-pre-wrap">
					<span class="font-medium text-gray-900">Comments:</span>
					{{ selectedProcedure.comments || "—" }}
				</p>
			</div>
		</template>
	</Dialog>

	<Dialog v-model="lab_open" :options="{ size: '6xl' }">
		<template #body-title>
			<div class="flex items-center justify-between gap-2">
				<h2 class="text-xl font-semibold text-gray-900">Lab Test</h2>
				<Button
					v-if="canPrintReport"
					theme="gray"
					size="sm"
					@click="printReport(labResult.order.diagnostic_report)"
				>
					<Tooltip :text="'Print Report'" placement="top">
						<FeatherIcon name="printer" class="size-3 text-ink-white-7" />
					</Tooltip>
				</Button>
			</div>
			<p class="py-2 text-sm text-gray-500"># {{ selectedLab.encounter }}</p>
		</template>
		<template #body-content>
			<div class="space-y-3 text-sm text-gray-700">
				<p><span class="font-medium text-gray-900">Test:</span> {{ selectedLab.lab_test_name || "—" }}</p>
				<p v-if="selectedLab.priority"><span class="font-medium text-gray-900">Priority:</span> {{ selectedLab.priority }}</p>
				<p><span class="font-medium text-gray-900">Practitioner:</span> {{ selectedLab.practitioner_name || "—" }}</p>
				<p><span class="font-medium text-gray-900">Ordered on:</span> {{ formatDate(selectedLab.encounter_date) }}</p>
				<p class="whitespace-pre-wrap">
					<span class="font-medium text-gray-900">Comments:</span>
					{{ selectedLab.comment || "—" }}
				</p>
			</div>

			<div v-if="showResults" class="mt-6">
				<div class="flex items-center justify-between gap-2 py-2">
					<h3 class="text-lg font-semibold text-gray-900">Result</h3>
					<Badge
						v-if="labResult?.order?.diagnostic_report_status"
						variant="outline"
						:theme="labResult.order.diagnostic_report_status == 'Approved' ? 'green' : 'orange'"
					>
						{{ labResult.order.diagnostic_report_status }}
					</Badge>
				</div>
				<div v-if="labResult?.test" class="space-y-2 max-h-[60vh] overflow-y-auto pr-2">
					<div class="bg-white rounded-xl shadow-md border overflow-hidden">
						<div class="px-4 py-3 bg-gray-50">
							<div class="flex items-center gap-2">
								<p class="font-medium text-gray-800 py-2">{{ labResult.test.observation_template }}</p>
								<Badge
									v-if="labResult.test.observation_status"
									variant="outline"
									size="sm"
									:theme="statusColor(labResult.test.observation_status)"
								>
									{{ labResult.test.observation_status || "Pending" }}
								</Badge>
							</div>
							<div class="divide-y divide-gray-200 border border-gray-200 rounded-lg">
								<div class="grid grid-cols-3 bg-gray-50 px-3 py-2 text-sm font-medium text-gray-700">
									<div>Test</div>
									<div>Result</div>
									<div>Reference</div>
								</div>
								<template v-if="labResult.test.children?.length">
									<div
										v-for="(comp, i) in labResult.test.children"
										:key="i"
										class="grid grid-cols-3 px-3 py-2 text-sm"
									>
										<div>
											<p class="font-medium text-gray-800">{{ comp.observation_template }}</p>
											<p v-if="comp.collection_date_time" class="text-xs text-gray-600">
												Collected On: {{ formatDateTime(comp.collection_date_time) }}
											</p>
										</div>
										<div class="font-semibold">{{ comp.result || "—" }} {{ comp.uom }}</div>
										<div v-html="comp.reference" class="text-gray-600"></div>
									</div>
								</template>
								<div v-else class="grid grid-cols-3 px-3 py-2 text-sm">
									<div>
										<p class="font-medium text-gray-800">{{ labResult.test.observation_template }}</p>
										<p v-if="labResult.test.collection_date_time" class="text-xs text-gray-600">
											Collected On: {{ formatDateTime(labResult.test.collection_date_time) }}
										</p>
									</div>
									<div class="font-semibold">{{ labResult.test.result || "—" }} {{ labResult.test.uom }}</div>
									<div v-html="labResult.test.reference" class="text-gray-600"></div>
								</div>
							</div>
						</div>
					</div>
				</div>
				<p v-else class="text-sm text-gray-500">Results are not available yet.</p>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { ref, computed, inject, watch } from 'vue'
import { createResource, Button, Dialog, Badge, Tooltip } from 'frappe-ui'

const healthcareSettings = inject('healthcareSettings', ref({}))

const listKind = ref('procedures')
const procedures = ref([])
const labs = ref([])
const proceduresLoaded = ref(false)
const labsLoaded = ref(false)
const diagnosticOrders = ref([])
const currentPage = ref(1)
const pageSize = 16

const procedure_open = ref(false)
const lab_open = ref(false)
const selectedProcedure = ref({})
const selectedLab = ref({})

const items = computed(() => (listKind.value === 'procedures' ? procedures.value : labs.value))
const listLoaded = computed(() => (listKind.value === 'procedures' ? proceduresLoaded.value : labsLoaded.value))

const emptyMessage = computed(() =>
	listKind.value === 'procedures'
		? "Looks like you don't have any prescribed procedures yet."
		: "Looks like you don't have any prescribed lab tests yet."
)

watch(listKind, () => {
	currentPage.value = 1
})

const getProcedures = createResource({
	url: '/api/method/healthcare.healthcare.api.patient_portal.get_procedure_orders',
	method: 'GET',
	onSuccess(response) {
		procedures.value = response || []
		proceduresLoaded.value = true
	},
	onError() {
		proceduresLoaded.value = true
	},
})
getProcedures.fetch()

const getLabs = createResource({
	url: '/api/method/healthcare.healthcare.api.patient_portal.get_lab_orders',
	method: 'GET',
	onSuccess(response) {
		labs.value = response || []
		labsLoaded.value = true
	},
	onError() {
		labsLoaded.value = true
	},
})
getLabs.fetch()

const getOrders = createResource({
	url: '/api/method/healthcare.healthcare.api.patient_portal.get_orders',
	method: 'GET',
	onSuccess(response) {
		diagnosticOrders.value = response || []
	},
})

watch(
	() => healthcareSettings.value?.show_diagnostics_tab,
	(show) => {
		if (show) getOrders.fetch()
	},
	{ immediate: true },
)

const showResults = computed(() => Boolean(healthcareSettings.value?.show_diagnostics_tab))

const labResult = computed(() => matchOrder(selectedLab.value?.service_request, diagnosticOrders.value))

const canPrintReport = computed(() => {
	const status = labResult.value?.order?.diagnostic_report_status
	return showResults.value && labResult.value?.order?.diagnostic_report && status && status !== 'Open'
})

function matchOrder(serviceRequest, orders) {
	if (!serviceRequest) return null
	for (const order of orders || []) {
		for (const test of order.tests || []) {
			if (test.service_request === serviceRequest) return { order, test }
			const child = (test.children || []).find((row) => row.service_request === serviceRequest)
			if (child) return { order, test }
		}
	}
	return null
}

function openItem(item) {
	if (listKind.value === 'procedures') {
		selectedProcedure.value = item
		procedure_open.value = true
		return
	}
	selectedLab.value = item
	lab_open.value = true
}

function itemTitle(item) {
	return listKind.value === 'procedures' ? item.procedure_name : item.lab_test_name
}

function itemComment(item) {
	return listKind.value === 'procedures' ? item.comments : item.comment
}

function formatDate(dateStr) {
	if (!dateStr) return '—'
	return new Date(dateStr).toLocaleDateString('en-IN', {
		weekday: 'long',
		year: 'numeric',
		month: 'long',
		day: 'numeric',
	})
}

function formatDateTime(dateStr) {
	if (!dateStr) return ''
	return new Date(dateStr).toLocaleString('en-IN', {
		year: 'numeric',
		month: 'short',
		day: 'numeric',
		hour: '2-digit',
		minute: '2-digit',
		hour12: false,
	})
}

function statusColor(status) {
	if (['Collected', 'Completed', 'Paid', 'Approved'].includes(status)) return 'green'
	if (['Pending', 'In Progress', 'Open', 'Partly Paid', 'Not Approved'].includes(status)) return 'orange'
	if (['Rejected', 'Cancelled', 'Unpaid'].includes(status)) return 'red'
	return 'gray'
}

function printReport(name) {
	const pdfOptions = JSON.stringify({
		'page-size': 'A4',
		'margin-top': '30mm',
		'margin-bottom': '30mm',
		'margin-left': '1mm',
		'margin-right': '1mm',
	})
	const w = window.open(
		'/api/method/healthcare.healthcare.api.patient_portal.download_pdf?' +
			'doctype=' + encodeURIComponent('Diagnostic Report') +
			'&name=' + encodeURIComponent(JSON.stringify([name])) +
			'&options=' + encodeURIComponent(pdfOptions)
	)
	if (!w) {
		alert('Please enable pop-ups')
	}
}

const totalPages = computed(() => Math.max(1, Math.ceil(items.value.length / pageSize)))

const paginatedItems = computed(() => {
	const start = (currentPage.value - 1) * pageSize
	return items.value.slice(start, start + pageSize)
})
</script>
