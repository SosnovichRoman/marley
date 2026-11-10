<template>
	<div class="py-4 relative min-h-[75vh] flex flex-col">
		<div v-if="!loaded" class="flex-1"></div>
		<div v-else-if="paginatedMedications.length" class="flex-1 overflow-y-auto p-2">
			<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
				<Card
					v-for="(item, index) in paginatedMedications"
					:key="`${item.encounter}-${item.drug_name}-${index}`"
					class="rounded-xl border border-gray-200 p-2 bg-surface-white
						min-h-[170px] min-w-[240px] !shadow-none drop-shadow-xl"
				>
					<p class="text-md font-semibold text-gray-800 truncate">
						{{ item.drug_name || "—" }}
					</p>
					<p class="mt-1 text-sm text-gray-700">{{ formatDosage(item) }}</p>
					<p v-if="item.period" class="mt-1 text-xs text-gray-600">{{ item.period }}</p>
					<p v-if="item.comment" class="mt-2 text-xs text-gray-600 line-clamp-2 whitespace-pre-wrap">
						{{ item.comment }}
					</p>
					<p class="mt-2 text-xs text-gray-500">
						<FeatherIcon name="calendar" class="inline w-3 h-3 mr-1 text-gray-500" />
						{{ formatDate(item.encounter_date) }}
					</p>
					<p class="mt-1 text-xs text-gray-500 truncate">
						{{ item.practitioner_name }}
					</p>
					<p class="mt-1 text-xs text-gray-400 truncate"># {{ item.encounter }}</p>
				</Card>
			</div>
		</div>

		<div v-else class="flex flex-col items-center justify-center flex-grow text-center p-6">
			<FeatherIcon name="file-text" class="w-12 h-12 text-gray-400 mb-3" />
			<h2 class="text-lg font-semibold text-gray-700">No Records Found</h2>
			<p class="text-sm text-gray-500">Looks like you don't have any prescribed medications yet.</p>
		</div>

		<div v-if="paginatedMedications.length" class="flex justify-center items-center space-x-2 mt-auto pt-2">
			<Button variant="subtle" :disabled="currentPage === 1" @click="currentPage--">Prev</Button>
			<span class="text-sm text-gray-600">Page {{ currentPage }} of {{ totalPages }}</span>
			<Button variant="subtle" :disabled="currentPage === totalPages" @click="currentPage++">Next</Button>
		</div>
	</div>

	<Dialog :options="{
		title: dialog_title,
		message: dialog_message,
		size: 'xl',
		icon: { name: 'alert-triangle', appearance: 'warning' },
		actions: [{ label: 'OK', variant: 'solid' }],
	}" v-model="alert_dialog" @click="alert_dialog = false" />
</template>

<script setup>
import { ref, computed } from 'vue'
import { createResource, Button, Dialog } from 'frappe-ui'

let alert_dialog = ref(false)
let medications = ref([])
const loaded = ref(false)
let dialog_title = ref('')
let dialog_message = ref('')
const currentPage = ref(1)
const pageSize = 16

const getMedications = createResource({
	url: '/api/method/healthcare.healthcare.api.patient_portal.get_medications',
	method: 'GET',
	onSuccess(response) {
		medications.value = response || []
		loaded.value = true
	},
	onError(error) {
		loaded.value = true
		dialog_message.value = error.messages?.[0] || error
		dialog_title.value = 'Failed to load medications'
		alert_dialog.value = true
	},
})
getMedications.fetch()

function formatDosage(row) {
	if (row.dosage_by_interval && row.interval) {
		return [row.interval, row.interval_uom].filter(Boolean).join(' ')
	}
	return [row.dosage, row.dosage_form].filter(Boolean).join(' · ') || '—'
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

const totalPages = computed(() => Math.max(1, Math.ceil(medications.value.length / pageSize)))

const paginatedMedications = computed(() => {
	const start = (currentPage.value - 1) * pageSize
	return medications.value.slice(start, start + pageSize)
})
</script>
