<template>
	<div class="py-4 relative min-h-[75vh] flex flex-col">
		<div v-if="!loaded" class="flex-1"></div>
		<div
			v-else-if="paginatedEncounters.length"
			class="flex-1 overflow-y-auto p-2"
		>
			<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
				<Card
					v-for="item in paginatedEncounters"
					:key="item.name"
					class="cursor-pointer rounded-xl border border-gray-200 transition-transform
						hover:scale-105 duration-200 hover:drop-shadow-md p-2 bg-surface-white
						min-h-[170px] min-w-[240px] !shadow-none drop-shadow-xl"
					@click="openEncounter(item.name)"
				>
					<div class="flex items-center justify-between whitespace-nowrap">
						<h3 class="text-xs font-medium text-gray-500 truncate">{{ item.name }}</h3>
					</div>
					<p class="mt-2 text-md font-semibold text-gray-800 truncate">
						{{ item.practitioner_name || "Visit" }}
					</p>
					<p v-if="item.medical_department" class="mt-1 text-xs text-gray-600 truncate">
						{{ item.medical_department }}
					</p>
					<p class="mt-1 text-xs text-gray-600 leading-snug break-words whitespace-normal">
						<FeatherIcon name="calendar" class="inline w-3 h-3 mr-1 text-gray-500" />
						{{ formatDate(item.encounter_date) }}
						<span v-if="item.encounter_time"> · {{ item.encounter_time }}</span>
					</p>
					<p v-if="item.diagnosis?.length" class="mt-2 text-xs text-gray-700 line-clamp-2">
						{{ item.diagnosis.join(", ") }}
					</p>
				</Card>
			</div>
		</div>

		<div
			v-else
			class="flex flex-col items-center justify-center flex-grow text-center p-6"
		>
			<FeatherIcon name="file-text" class="w-12 h-12 text-gray-400 mb-3" />
			<h2 class="text-lg font-semibold text-gray-700">No Records Found</h2>
			<p class="text-sm text-gray-500">Looks like you don't have any visits yet.</p>
		</div>

		<div v-if="paginatedEncounters.length" class="flex justify-center items-center space-x-2 mt-auto pt-2">
			<Button variant="subtle" :disabled="currentPage === 1" @click="currentPage--">
				Prev
			</Button>
			<span class="text-sm text-gray-600">
				Page {{ currentPage }} of {{ totalPages }}
			</span>
			<Button variant="subtle" :disabled="currentPage === totalPages" @click="currentPage++">
				Next
			</Button>
		</div>
	</div>

	<Dialog v-model="details_open" :options="{ size: '4xl' }">
		<template #body-title>
			<div>
				<h2 class="text-xl font-semibold text-gray-900">Visit Details</h2>
			</div>
			<div class="py-2 flex items-center justify-between gap-2">
				<p class="text-sm text-gray-500"># {{ selectedEncounter.name }}</p>
				<Button theme="gray" size="md" @click="printEncounter(selectedEncounter.name)">
					<Tooltip :text="'Print Prescription'" placement="top">
						<FeatherIcon name="printer" class="size-4 text-ink-white-7" />
					</Tooltip>
				</Button>
			</div>
		</template>
		<template #body-content>
			<div class="rounded-xl shadow-sm py-2 bg-gray-50 space-y-4">
				<div class="grid grid-cols-1 md:grid-cols-2 gap-6 px-2">
					<div>
						<h3 class="text-gray-700 font-medium">When</h3>
						<p class="mt-1 text-lg font-semibold text-gray-900">
							{{ formatDate(selectedEncounter.encounter_date) }}
						</p>
						<p v-if="selectedEncounter.encounter_time" class="mt-1 text-sm text-gray-600">
							{{ selectedEncounter.encounter_time }}
						</p>
					</div>
					<div>
						<h3 class="text-gray-700 font-medium">Practitioner</h3>
						<p class="mt-1 text-lg font-semibold text-gray-900">
							{{ selectedEncounter.practitioner_name || "—" }}
						</p>
						<p class="mt-1 text-sm text-gray-600">
							{{ selectedEncounter.medical_department || "—" }}
						</p>
					</div>
				</div>

				<section class="px-2">
					<h3 class="text-gray-700 font-medium">Symptoms</h3>
					<p class="mt-1 text-sm text-gray-800 whitespace-pre-wrap">
						{{ joinList(selectedEncounter.symptoms) }}
					</p>
				</section>
				<section class="px-2">
					<h3 class="text-gray-700 font-medium">Diagnosis</h3>
					<p class="mt-1 text-sm text-gray-800 whitespace-pre-wrap">
						{{ joinList(selectedEncounter.diagnosis) }}
					</p>
				</section>
				<section class="px-2">
					<h3 class="text-gray-700 font-medium">Notes</h3>
					<p class="mt-1 text-sm text-gray-800 whitespace-pre-wrap">
						{{ selectedEncounter.encounter_comment || "—" }}
					</p>
				</section>

				<section class="px-2">
					<h3 class="text-gray-700 font-medium">Medications</h3>
					<ul v-if="selectedEncounter.medications?.length" class="mt-2 space-y-2">
						<li
							v-for="(row, index) in selectedEncounter.medications"
							:key="index"
							class="rounded-lg border border-gray-200 bg-white px-3 py-2"
						>
							<p class="font-medium text-gray-900">{{ row.drug_name || "—" }}</p>
							<p class="text-sm text-gray-600">{{ formatDosage(row) }}</p>
							<p v-if="row.period" class="text-sm text-gray-600">{{ row.period }}</p>
							<p v-if="row.comment" class="text-sm text-gray-600 whitespace-pre-wrap">{{ row.comment }}</p>
						</li>
					</ul>
					<p v-else class="mt-1 text-sm text-gray-500">None</p>
				</section>

				<section class="px-2">
					<h3 class="text-gray-700 font-medium">Procedures</h3>
					<ul v-if="selectedEncounter.procedures?.length" class="mt-2 space-y-2">
						<li
							v-for="(row, index) in selectedEncounter.procedures"
							:key="index"
							class="rounded-lg border border-gray-200 bg-white px-3 py-2"
						>
							<p class="font-medium text-gray-900">{{ row.procedure_name }}</p>
							<p class="text-sm text-gray-600">
								<span v-if="row.date">{{ formatDate(row.date) }}</span>
								<span v-if="row.no_of_sessions"> · {{ row.no_of_sessions }} sessions</span>
							</p>
							<p v-if="row.comments" class="text-sm text-gray-600">{{ row.comments }}</p>
						</li>
					</ul>
					<p v-else class="mt-1 text-sm text-gray-500">None</p>
				</section>

				<section class="px-2 pb-2">
					<h3 class="text-gray-700 font-medium">Lab Tests</h3>
					<ul v-if="selectedEncounter.lab_tests?.length" class="mt-2 space-y-2">
						<li
							v-for="(row, index) in selectedEncounter.lab_tests"
							:key="index"
							class="rounded-lg border border-gray-200 bg-white px-3 py-2"
						>
							<p class="font-medium text-gray-900">{{ row.lab_test_name || "—" }}</p>
							<p v-if="row.priority" class="text-sm text-gray-600">{{ row.priority }}</p>
							<p v-if="row.comment" class="text-sm text-gray-600 whitespace-pre-wrap">{{ row.comment }}</p>
						</li>
					</ul>
					<p v-else class="mt-1 text-sm text-gray-500">None</p>
				</section>
			</div>
		</template>
	</Dialog>

	<Dialog :options="{
		title: dialog_title,
		message: dialog_message,
		size: 'xl',
		icon: { name: 'alert-triangle', appearance: 'warning' },
		actions: [{ label: 'OK', variant: 'solid' }],
	}" v-model="alert_dialog" @click="alert_dialog = false" />
</template>

<script setup>
import { ref, computed, inject, watch } from 'vue'
import { createResource, Button, Dialog, Tooltip } from 'frappe-ui'

const requestedEncounter = inject('requestedEncounter', ref(null))

let details_open = ref(false)
let alert_dialog = ref(false)
let encounters = ref([])
const loaded = ref(false)
let selectedEncounter = ref({})
let dialog_title = ref('')
let dialog_message = ref('')

const currentPage = ref(1)
const pageSize = 16

const getEncounters = createResource({
	url: '/api/method/healthcare.healthcare.api.patient_portal.get_encounters',
	method: 'GET',
	onSuccess(response) {
		encounters.value = response || []
		loaded.value = true
	},
	onError(error) {
		loaded.value = true
		dialog_message.value = error.messages?.[0] || error
		dialog_title.value = 'Failed to load visits'
		alert_dialog.value = true
	},
})
getEncounters.fetch()

const encounterDetail = createResource({
	url: '/api/method/healthcare.healthcare.api.patient_portal.get_encounter',
	method: 'GET',
	makeParams() {
		return { name: pendingName.value }
	},
	onSuccess(response) {
		selectedEncounter.value = response || {}
		details_open.value = true
	},
	onError(error) {
		dialog_message.value = error.messages?.[0] || error
		dialog_title.value = 'Failed to load visit'
		alert_dialog.value = true
	},
})

const pendingName = ref(null)

function openEncounter(name) {
	if (!name) return
	pendingName.value = name
	encounterDetail.fetch()
}

watch(requestedEncounter, (name) => {
	if (!name) return
	requestedEncounter.value = null
	openEncounter(name)
}, { immediate: true })

function joinList(values) {
	if (!values || !values.length) return '—'
	return values.join(', ')
}

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

function printEncounter(name) {
	const pdfOptions = JSON.stringify({
		'page-size': 'A4',
		'margin-top': '60mm',
		'margin-bottom': '60mm',
		'margin-left': '5mm',
		'margin-right': '5mm',
	})
	const w = window.open(
		'/api/method/healthcare.healthcare.api.patient_portal.download_pdf?' +
			'doctype=' + encodeURIComponent('Patient Encounter') +
			'&name=' + encodeURIComponent(JSON.stringify([name])) +
			'&options=' + encodeURIComponent(pdfOptions)
	)
	if (!w) {
		alert('Please enable pop-ups')
	}
}

const totalPages = computed(() => Math.max(1, Math.ceil(encounters.value.length / pageSize)))

const paginatedEncounters = computed(() => {
	const start = (currentPage.value - 1) * pageSize
	return encounters.value.slice(start, start + pageSize)
})
</script>
